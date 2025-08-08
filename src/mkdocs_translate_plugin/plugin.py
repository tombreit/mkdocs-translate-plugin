# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

"""
MkDocs Translate Plugin
"""

import re
from pathlib import Path
from typing import Literal

import mkdocs

from .log import logger
from .translation_services import translate_content


class TranslatePluginConfig(mkdocs.config.base.Config):
    translation_service = mkdocs.config.config_options.Choice(
        choices=["saia", "deepl", "simpleen"]
    )
    translation_service_api_key = mkdocs.config.config_options.Type(str)


class TranslatePlugin(mkdocs.plugins.BasePlugin[TranslatePluginConfig]):
    def __init__(self):
        self.is_serve = False

    def on_startup(
        self, *, command: Literal["build", "gh-deploy", "serve"], dirty: bool
    ) -> None:
        self.is_serve = command == "serve"

    def add_translation_notice(
        self, content: str, source_lang: str, target_lang: str
    ) -> str:
        """
        Add a translation notice to the markdown content after any frontmatter block.

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
        if self.theme_name == "material":
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
        frontmatter_match = re.match(r"^---\n.*?\n---\n", content, re.DOTALL)

        if frontmatter_match:
            # Insert notice after frontmatter
            frontmatter = frontmatter_match.group(0)
            content_after_frontmatter = content[len(frontmatter) :]
            return frontmatter + translation_notice + content_after_frontmatter
        else:
            # No frontmatter, add notice at the top
            return translation_notice + content

    def on_pre_build(self, config):
        """Translate files before build process starts"""

        if self.is_serve:
            logger.info(
                "Plugin deactivated during `serve`. Only active during `build`."
            )
            return

        # Current run language. The mkdocs-static-i18n processes the
        # on_pre_build hook for each language, but we only neet to
        # trigger the translation for the default source language.
        i18n_plugin = config.plugins.get("i18n")
        current_language = config.theme.get("language")

        if current_language != i18n_plugin.default_language:
            logger.debug(
                f"Skipping on_pre_build hook: language '{current_language}' is not default language '{i18n_plugin.default_language}'"
            )
            return

        target_translations = [
            lang
            for lang in i18n_plugin.all_languages
            if lang != i18n_plugin.default_language
        ]

        # Get source language file suffix
        source_language_suffix = f".{i18n_plugin.default_language}.md"

        docs_dir = Path(config["docs_dir"])
        for filepath in docs_dir.rglob("*.md"):
            rel_filepath = filepath.relative_to(docs_dir.parent)

            if rel_filepath.name.endswith(source_language_suffix):
                logger.info(
                    f"Source language file: {rel_filepath.name}, checking for translations..."
                )

                # Test if a translation file for each target language exists and
                # if not, create it
                for lang in target_translations:
                    target_suffix = f".{lang}.md"
                    target_filename = filepath.name.replace(
                        source_language_suffix, target_suffix
                    )
                    target_filepath = filepath.parent / target_filename
                    target_filepath = target_filepath.relative_to(docs_dir.parent)

                    if target_filepath.exists():
                        logger.info(
                            f"Translation file already exists: {target_filepath.name}. Skipping..."
                        )
                    else:
                        logger.info(
                            f"🔥 Translating {rel_filepath} to {target_filepath}..."
                        )
                        source_content = filepath.read_text(encoding="utf-8")
                        source_lang = i18n_plugin.default_language
                        target_lang = lang

                        translated_content = translate_content(
                            config=self.config,
                            content=source_content,
                            source_lang=source_lang,
                            target_lang=target_lang,
                            logger=logger,
                        )

                        if translated_content:
                            # Add translation notice to the content
                            translated_content_with_notice = (
                                self.add_translation_notice(
                                    translated_content,
                                    source_lang=source_lang,
                                    target_lang=target_lang,
                                )
                            )

                            # Write the modified content to the file
                            new_path = filepath.parent / target_filename
                            new_path.write_text(
                                translated_content_with_notice, encoding="utf-8"
                            )
                        else:
                            logger.warning(
                                f"Translation failed for {rel_filepath.name} to {target_filename}"
                            )

    def on_config(self, config):
        """Store configuration settings for later use"""
        self.theme_name = config.theme.name
        logger.debug(f"Configured with theme: {self.theme_name}")
        return config
