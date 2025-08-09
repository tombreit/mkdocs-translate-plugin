# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT


import pytest
from mkdocs_translate_plugin.helpers import add_translation_notice, notice_formats


@pytest.mark.parametrize(
    "theme_name,source_lang,target_lang",
    [
        ("material", "en", "de"),
        ("default", "en", "fr"),
        ("unknown_theme", "en", "es"),
    ],
)
def test_add_translation_notice_reuses_notice_format(
    theme_name, source_lang, target_lang
):
    content = "# Heading\nContent."
    expected_format = notice_formats.get(theme_name, notice_formats["default"])
    expected_notice = expected_format.format(
        source_lang=source_lang.upper(), target_lang=target_lang.upper()
    )
    result = add_translation_notice(content, source_lang, target_lang, theme_name)
    assert expected_notice in result


@pytest.mark.parametrize(
    "content,theme_name,source_lang,target_lang,expected_prefix",
    [
        # Case 1: Frontmatter and level 1 heading
        (
            "---\ntitle: Test\n---\n# Heading\nSome content.",
            "material",
            "en",
            "de",
            "# Heading\n",
        ),
        # Case 2: Only frontmatter, no heading
        (
            "---\ntitle: Test\n---\nSome content without heading.",
            "default",
            "en",
            "de",
            "---\ntitle: Test\n---\n",
        ),
        # Case 3: No heading, no frontmatter
        (
            "Just some content.",
            "default",
            "en",
            "de",
            None,
        ),
        # Case 4: A level 1 heading somewhere, no frontmatter
        (
            "Just some content.\n# A heading in the middle of nowhere\nMore content.",
            "default",
            "en",
            "de",
            "# A heading in the middle of nowhere\n",
        ),
    ],
)
def test_add_translation_notice_combined(
    content, theme_name, source_lang, target_lang, expected_prefix
):
    expected_format = notice_formats.get(theme_name, notice_formats["default"])
    expected_notice = expected_format.format(
        source_lang=source_lang.upper(), target_lang=target_lang.upper()
    )
    result = add_translation_notice(content, source_lang, target_lang, theme_name)

    if expected_prefix:
        # The notice must directly follow the expected prefix
        expected_combined = expected_prefix + expected_notice
        assert expected_combined in result
    else:
        # The notice must be at the very top
        assert result.startswith(expected_notice)
