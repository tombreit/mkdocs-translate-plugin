# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import re
from typing import Optional


notice_formats = {
    "material": "\n!!! note\n    This document was automatically translated from {source_lang} to {target_lang}.\n\n",
    "default": "\n>NOTE:\nThis document was automatically translated from {source_lang} to {target_lang}.\n\n",
}


def add_translation_notice(
    content: str, source_lang: str, target_lang: str, theme_name: str
) -> str:
    """
    Add a translation notice to the markdown content after first level 1 header.
    """

    notice_format = notice_formats.get(theme_name, notice_formats["default"])
    translation_notice = notice_format.format(
        source_lang=source_lang.upper(), target_lang=target_lang.upper()
    )

    # 1. Insert after the first level 1 heading (anywhere in the file)
    heading_match = re.search(r"(^# .+\n)", content, re.MULTILINE)
    if heading_match:
        end = heading_match.end(1)
        return content[:end] + translation_notice + content[end:]

    # 2. If no heading, but frontmatter at the start, insert after frontmatter
    frontmatter_match = re.match(r"^(---\n.*?\n---\n)", content, re.DOTALL)
    if frontmatter_match:
        frontmatter = frontmatter_match.group(1)
        rest = content[len(frontmatter) :]
        return frontmatter + translation_notice + rest

    # 3. Otherwise, insert at the very top
    return translation_notice + content


def code_block_transform(
    content: str, code_blocks: Optional[list[str]] = None, mode: str = "protect"
) -> str | tuple[str, list[str]]:
    """
    Protect or restore code blocks in markdown content.

    Perhaps this would be simpler as a good system prompt...

    - In 'protect' mode: replaces code blocks with placeholders and returns (content_with_placeholders, code_blocks).
    - In 'restore' mode: replaces placeholders in content with code_blocks and returns the restored content.

    Args:
        content: The markdown content.
        code_blocks: The list of code blocks (required for 'restore' mode).
        mode: 'protect' or 'restore'.

    Returns:
        In 'protect' mode: (content_with_placeholders, code_blocks)
        In 'restore' mode: restored_content
    """
    pattern = r"```[a-z]*\n[\s\S]*?\n```"

    if mode == "protect":
        code_blocks = []

        def replace_code_block(match):
            code_blocks.append(match.group(0))
            return f"CODEBLOCK_{len(code_blocks) - 1}_PLACEHOLDER"

        content_with_placeholders = re.sub(pattern, replace_code_block, content)
        return content_with_placeholders, code_blocks

    elif mode == "restore":
        if code_blocks is None:
            raise ValueError("code_blocks must be provided in restore mode")
        for i, block in enumerate(code_blocks):
            content = content.replace(f"CODEBLOCK_{i}_PLACEHOLDER", block)
        return content

    else:
        raise ValueError("mode must be 'protect' or 'restore'")
