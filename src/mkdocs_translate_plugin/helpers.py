# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import re

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
