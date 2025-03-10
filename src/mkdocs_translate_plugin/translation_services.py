# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import json
import sys
import re

import requests
import pypandoc
import mkdocs
import deepl
from openai import OpenAI
from markdownify import markdownify as md
from markdown import markdown


logger = mkdocs.plugins.get_plugin_logger(__name__)


def translate_content(config, content: str, source_lang: str, target_lang: str) -> str:
    """
    Translate content using configured service
    Valid translations services are already checked in the plugin configuration
    """
    translation_func_name = f"translate_with_{config.translation_service.lower()}"
    translation_func = getattr(sys.modules[__name__], translation_func_name)

    return translation_func(config, content, source_lang, target_lang)


def translate_with_simpleen(config, content, source_lang, target_lang):
    """Translate content using Simpleen API"""
    translated_text = None

    url = f"https://api.simpleen.io/translate?auth_key={config.translation_service_api_key}"
    headers = {"Accept": "application/json", "Content-Type": "application/json"}

    payload = {
        "dataformat": "Markdown",
        "source_language": source_lang.upper(),
        "target_language": target_lang.upper(),
        "text": content,
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()  # Raise an exception for HTTP errors
        translated_text = response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Simpleen API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")

    return translated_text


# def translate_with_openai(
#     config, content: str, source_lang: str, target_lang: str
# ) -> str:
#     """Translate using OpenAI's ChatGPT API"""

#     client = OpenAI(
#         api_key=config.translation_service_api_key,
#         base_url="https://chat-ai.academiccloud.de/v1",
#     )

#     developer_prompt = (
#         "You are a professional translator proficient in technical documentation and Markdown syntax.\n"
#         "Preserve the markdown formatting and structure.\n"
#         "Do not translate code blocks or inline code.\n"
#         "Be aware of markdowns whitespace sensitivity, like preserving trailing spaces on lines: if a line ends with two spaces, these two spaces need to be preserved.\n"
#     )

#     user_prompt = f"Translate the following markdown content from {source_lang.upper()} to {target_lang.upper()}: {content}"

#     try:
#         chat_completion = client.chat.completions.create(
#             model="llama-3.1-sauerkrautlm-70b-instruct",
#             messages=[
#                 {
#                     "role": "developer",
#                     "content": developer_prompt,
#                 },
#                 {
#                     "role": "user",
#                     "content": user_prompt,
#                 },
#             ],
#             temperature=0,
#         )
#         print(f"Chat completion: {chat_completion}")
#         translated_text = chat_completion.choices[0].message.content
#         return translated_text.strip()
#     except Exception as e:
#         print(f"Translation error: {e}")
#         return None


def translate_with_chatai(
    config, content: str, source_lang: str, target_lang: str
) -> str:
    """
    Translate markdown content using an OpenAI-compatible API while preserving formatting.

    This function uses detailed prompting to instruct the LLM to preserve all markdown
    elements including code blocks, links, headers, lists, and special formatting.

    https://docs.hpc.gwdg.de/services/chat-ai/models/index.html
    https://docs.hpc.gwdg.de/services/saia/index.html
    """

    # Initialize OpenAI client with the configured API key and base URL
    client = OpenAI(
        api_key=config.translation_service_api_key,
        base_url="https://chat-ai.academiccloud.de/v1",
    )

    # Protect code blocks before translation
    code_blocks = []
    pattern = r"```[a-z]*\n[\s\S]*?\n```"

    def replace_code_block(match):
        code_blocks.append(match.group(0))
        return f"CODEBLOCK_{len(code_blocks)-1}_PLACEHOLDER"

    # Replace code blocks with placeholders
    content_with_placeholders = re.sub(pattern, replace_code_block, content)

    # Create a detailed system prompt for precise instructions
    system_prompt = (
        "You are an expert translator specialized in technical documentation. "
        "Your task is to translate markdown content while perfectly preserving ALL markdown formatting and structure. "
        "\n\nRULES TO STRICTLY FOLLOW:"
        "\n1. Keep all headers (# Heading) with the exact same level"
        "\n2. Preserve all bullet points and numbered lists with their original indentation"
        "\n3. Keep all hyperlinks in format [text](url) - translate only the text part, NOT the URL"
        "\n4. Keep all images in format ![alt text](url) - translate only the alt text part"
        "\n5. Keep all blockquotes (lines starting with >) with their original nesting level"
        "\n6. Preserve all inline formatting: **bold**, *italic*, `code`, ~~strikethrough~~"
        "\n7. Keep all tables with their original structure, including | and - characters"
        "\n8. Preserve all horizontal rules (---)"
        "\n9. Keep all line breaks, including trailing double spaces for forced line breaks"
        "\n10. DO NOT add or remove any markdown elements or structure"
        "\n11. DO NOT translate content inside placeholders marked as CODEBLOCK_X_PLACEHOLDER"
        "\n12. ALWAYS maintain the exact same document structure"
        "\n\nThis is critically important documentation that must maintain its exact structure."
    )

    # Create a user prompt with the content to translate
    user_prompt = (
        f"Translate the following markdown content from {source_lang.upper()} to {target_lang.upper()}. "
        f"Remember to follow ALL the rules about preserving markdown formatting:\n\n{content_with_placeholders}"
    )

    # Models suitable for precise instruction following (largest first)
    models = [
        "meta-llama-3.1-70b-instruct",  # Large model, good at following instructions
        "llama-3.1-sauerkrautlm-70b-instruct",  # Current model
        "mistral-large-instruct",  # Known for precision
        "qwen-2.5-72b-instruct",  # Another large model option
        "codestral-22b",  # May be good for technical content
    ]

    # Try models in order until successful
    translated_text = None
    errors = []

    for model in models:
        try:
            logger.info(f"Attempting translation with model: {model}")

            chat_completion = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0,  # Use 0 for more deterministic output
                max_tokens=90000,  # Adjust based on content length
            )

            translated_text = chat_completion.choices[0].message.content
            logger.info(f"Successfully translated with model: {model}")
            break

        except Exception as e:
            error_msg = f"Error with model {model}: {str(e)}"
            logger.warning(error_msg)
            errors.append(error_msg)
            continue

    if translated_text is None:
        logger.error(f"All translation attempts failed: {'; '.join(errors)}")
        return None

    # Restore code blocks
    for i, block in enumerate(code_blocks):
        translated_text = translated_text.replace(f"CODEBLOCK_{i}_PLACEHOLDER", block)

    # Additional verification of markdown integrity
    expected_elements = {
        "headers": len(re.findall(r"^#+\s", content, re.MULTILINE)),
        "code_blocks": len(re.findall(r"```", content)) // 2,
        "links": len(re.findall(r"\[.+?\]\(.+?\)", content)),
    }

    actual_elements = {
        "headers": len(re.findall(r"^#+\s", translated_text, re.MULTILINE)),
        "code_blocks": len(re.findall(r"```", translated_text)) // 2,
        "links": len(re.findall(r"\[.+?\]\(.+?\)", translated_text)),
    }

    # Log if there's a mismatch in markdown elements
    if expected_elements != actual_elements:
        logger.warning(
            f"Possible markdown corruption detected. "
            f"Expected: {expected_elements}, Got: {actual_elements}"
        )

    return translated_text.strip()


def translate_with_deepl(
    config, content: str, source_lang: str, target_lang: str
) -> str:
    """
    Translate markdown content using DeepL API with HTML round-tripping
    to preserve formatting.
    """
    # Convert markdown (including frontmatter) to HTML
    try:
        html_content = markdown(
            content,
            extensions=["meta", "tables", "fenced_code", "attr_list", "def_list"],
            output_format="html",
        )

        print(f"{html_content=}")

    except RuntimeError as e:
        print(f"Conversion error: {e}")
        return None

    auth_key = config.translation_service_api_key
    translator = deepl.Translator(auth_key)

    try:
        # Translate HTML content using DeepL API
        result = translator.translate_text(
            html_content,
            source_lang=source_lang.upper(),
            target_lang=target_lang.upper(),
            tag_handling="html",
            outline_detection=False,  # Disable to preserve HTML structure
            preserve_formatting=True,
            # split_sentences="nonewlines",
        )

        translated_html = result.text
        print(f"{translated_html=}")

        # Convert translated HTML back to markdown
        # translated_markdown = pypandoc.convert_text(
        #     translated_html, "gfm", format="html", extra_args=["--wrap=none"]
        # )
        translated_markdown = md(translated_html)

        return translated_markdown

    except Exception as e:
        print(f"Translation error: {e}")
        return None
