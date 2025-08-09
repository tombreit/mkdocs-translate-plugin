# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import re


def add_translation_notice(
    content: str, source_lang: str, target_lang: str, theme_name: str
) -> str:
    """
    Add a translation notice to the markdown content after first level 1 header
    Previously we added it after the frontmatter, but that broke
    MkDocs logic to determine the document title:
    > The "title" to use for the document.
    > A level 1 Markdown header on the first line of the document body.
    https://www.mkdocs.org/user-guide/writing-your-docs/#meta-data
    So we need to add the notice after the first level 1 header.

    Args:
        content: The translated markdown content
        source_lang: Source language code
        target_lang: Target language code

    Returns:
        Modified content with translation notice
    """

    # Check if theme has certain features
    # has_tabs = config.theme.has_feature("tabs")

    # Customize translation notice based on theme
    if theme_name == "material":
        # Use Material for MkDocs admonitions
        notice_format = "\n!!! note\n    This document was automatically translated from {source_lang} to {target_lang}.\n\n"
    else:
        # Use generic notice format
        notice_format = "\n>NOTE:\nThis document was automatically translated from {source_lang} to {target_lang}.\n\n"

    # Use the theme-specific notice format
    translation_notice = notice_format.format(
        source_lang=source_lang.upper(), target_lang=target_lang.upper()
    )

    # Check if content has frontmatter (enclosed by ---)
    # notice_anchor_match = re.match(r"^---\n.*?\n---\n", content, re.DOTALL)  # Use frontmatter block
    notice_anchor_match = re.match(r"^# .+\n", content)  # Use level 1 heading
    print(f"{notice_anchor_match=}")

    if notice_anchor_match:
        # Insert notice after notice_anchor_match
        anchor = notice_anchor_match.group(0)
        content_after_anchor = content[len(anchor) :]
        return anchor + translation_notice + content_after_anchor
    else:
        # No anchor, add notice at the top
        return translation_notice + content
