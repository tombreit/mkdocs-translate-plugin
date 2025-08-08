# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import re
import time
from openai import OpenAI
from mkdocs.plugins import PrefixedLogger


# SAIA supported models
# https://docs.hpc.gwdg.de/services/chat-ai/models/index.html

# teuken-7b-instruct-research: European languages
# mistral-large-instruct: Good overall performance, coding and multilingual reasoning
# qwen3-32b: Good overall performance, multilingual, global affairs, logic
# qwen3-235b-a22b: Great overall performance, reasoning
# openai-gpt-oss-120b
LLM = "openai-gpt-oss-120b"


def translate_with_saia(
    config, content: str, source_lang: str, target_lang: str, logger: PrefixedLogger
) -> str:
    """
    Translate markdown content using an OpenAI-compatible API while preserving formatting.

    This function uses detailed prompting to instruct the LLM to preserve all markdown
    elements including code blocks, links, headers, lists, and special formatting.

    https://docs.hpc.gwdg.de/services/chat-ai/models/index.html
    https://docs.hpc.gwdg.de/services/saia/index.html
    """

    client = OpenAI(
        api_key=config.translation_service_api_key,
        base_url="https://chat-ai.academiccloud.de/v1",
    )

    # Protect code blocks before translation
    code_blocks = []
    pattern = r"```[a-z]*\n[\s\S]*?\n```"

    def replace_code_block(match):
        code_blocks.append(match.group(0))
        return f"CODEBLOCK_{len(code_blocks) - 1}_PLACEHOLDER"

    # Replace code blocks with placeholders
    content_with_placeholders = re.sub(pattern, replace_code_block, content)

    # System prompt for precise instructions
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
        "\n13. ALWAYS end the translated content with blank line"
        "\n\nThis is critically important documentation that must maintain its exact structure."
    )

    # User prompt with the content to translate
    user_prompt = (
        f"Translate the following markdown content from {source_lang.upper()} to {target_lang.upper()}. "
        f"Remember to follow ALL the rules about preserving markdown formatting:\n\n{content_with_placeholders}"
    )

    translated_text = None
    errors = []

    try:
        logger.debug(f"Attempting translation with model: {LLM}")

        start_time = time.time()  # Start timing

        chat_completion = client.chat.completions.create(
            model=LLM,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,  # Use 0 for more deterministic output
            top_p=0.3,
            presence_penalty=0.0,
            # max_tokens=8192,  # Adjust based on content length
            extra_body={
                "chat_template_kwargs": {"enable_thinking": False},
            },
        )

        duration = time.time() - start_time  # End timing
        logger.debug(f"API response time: {duration:.2f} seconds")

        translated_text = chat_completion.choices[0].message.content
        logger.debug(f"Successfully translated with model: {LLM}")

        logger.info(f"✅ LLM: {LLM}; Duration: {duration:.2f} seconds;")

    except Exception as e:
        error_msg = f"Error with model {LLM}: {str(e)}"
        logger.warning(error_msg)
        errors.append(error_msg)

    if translated_text is None:
        logger.error(f"All translation attempts failed: {'; '.join(errors)}")
        return ""

    # If there is a reasoning or explanation, drop it. This ouput is enclosed in `<think></think>` tags.
    reasoning_match = re.search(r"<think>(.*?)</think>", translated_text, re.DOTALL)
    if reasoning_match:
        translated_text = translated_text.replace(reasoning_match.group(0), "")
        logger.info(f"Extracted reasoning: {reasoning_match.group(1)}")

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
