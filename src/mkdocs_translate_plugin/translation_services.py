import json
import sys
import requests
import pypandoc
import deepl
from openai import OpenAI


def translate_content(config, content: str, source_lang: str, target_lang: str) -> str:
    """
    Translate content using configured service
    Valid translations services are already checked in the plugin configuration
    """
    translation_func_name = f"translate_with_{config.translation_service.lower()}"
    translation_func = getattr(sys.modules[__name__], translation_func_name)
    translation_func(config, content, source_lang, target_lang)


def translate_with_simpleen(config, content, source_lang, target_lang):
    """Translate content using Simpleen API"""

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
        return translated_text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Simpleen API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")


def translate_with_openai(
    config, content: str, source_lang: str, target_lang: str
) -> str:
    """Translate using OpenAI's ChatGPT API"""

    client = OpenAI(
        api_key=config.translation_service_api_key,
        base_url="https://chat-ai.academiccloud.de/v1",
    )

    prompt = (
        f"Translate the following markdown content from {source_lang} to {target_lang}.\n"
        f"Preserve the markdown formatting and structure.\n"
        f"Do not translate code blocks or inline code.\n"
        f"Keep all markdown syntax intact.\n"
        f"Content:\n{content}\n"
        f"Translation:"
    )

    try:
        chat_completion = client.chat.completions.create(
            model="llama-3.1-sauerkrautlm-70b-instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a professional translator proficient in technical documentation and Markdown syntax.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
        )
        print(f"Chat completion: {chat_completion}")
        translated_text = chat_completion.choices[0].message.content
        return translated_text.strip()
    except Exception as e:
        print(f"Translation error: {e}")
        return None


def translate_with_deepl(
    config, content: str, source_lang: str, target_lang: str
) -> str:
    """
    Translate markdown content using DeepL API with HTML round-tripping
    to preserve formatting.
    """
    # Convert markdown (including frontmatter) to HTML
    try:
        html_content = pypandoc.convert_text(
            content,
            "html",
            format="markdown-markdown_in_html_blocks+four_space_rule+hard_line_breaks+yaml_metadata_block",
            extra_args=["--no-highlight", "--wrap=none"],
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
        translated_markdown = pypandoc.convert_text(
            translated_html, "gfm", format="html", extra_args=["--wrap=none"]
        )

        return translated_markdown

    except Exception as e:
        print(f"Translation error: {e}")
        return None
