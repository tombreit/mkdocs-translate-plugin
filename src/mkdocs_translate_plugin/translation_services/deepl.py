# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import logging
from typing import cast
import deepl
from markdown import markdown
from markdownify import markdownify as md
# import pypandoc


def translate_with_deepl(
    config, content: str, source_lang: str, target_lang: str, logger: logging.Logger
) -> str:
    """
    Translate markdown content using DeepL API with HTML round-tripping
    to preserve formatting.
    """
    logger.warning("DeepL translation service is largely untestet.")

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
        return ""

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

        # deepl.Translator.translate_text() can return either a single
        # TextResult or a list of TextResult objects, depending on the input.
        # Tell mypy this is always a TextResult, not a list
        result = cast(deepl.TextResult, result)
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
        return ""
