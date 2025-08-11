# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

"""
MkDocs Translate Plugin
"""

from pathlib import Path
from typing import Literal

import mkdocs
from mkdocs.plugins import BasePlugin
from mkdocs.config.defaults import MkDocsConfig

from .log import logger
from .helpers import add_translation_notice
from .translation_services import translate_content


class TranslatePluginConfig(mkdocs.config.base.Config):
    translation_service = mkdocs.config.config_options.Choice(
        choices=["saia", "deepl", "simpleen"]
    )
    # Making translation_service_api_key optional allow running in CI/CD
    # environments without an API key.
    translation_service_api_key = mkdocs.config.config_options.Type(str, default="")


class TranslatePlugin(BasePlugin[TranslatePluginConfig]):
    def __init__(self):
        self.is_serve = False

    def on_startup(
        self, *, command: Literal["build", "gh-deploy", "serve"], dirty: bool
    ) -> None:
        self.is_serve = command == "serve"

    def on_config(self, config: MkDocsConfig, **kwargs) -> MkDocsConfig:
        """Store configuration settings for later use"""
        self.theme_name = config.theme.name or "mkdocs"  # "mkdocs" is the default theme
        logger.debug(f"Configured with theme: {self.theme_name}")
        return config

    def on_pre_build(self, config: MkDocsConfig, **kwargs) -> None:
        """Translate files before build process starts"""

        if self.is_serve:
            logger.info(
                "Plugin deactivated during `serve`. Only active during `build`."
            )
            return

        if not self.config.translation_service_api_key:
            logger.info("🤷 No API key provided. Skipping translation.")
            return

        # Current run language. The mkdocs-static-i18n processes the
        # on_pre_build hook for each language, but we only neet to
        # trigger the translation for the default source language.
        i18n_plugin = config.plugins.get("i18n")
        current_language = config.theme.get("language")

        if not i18n_plugin or not hasattr(i18n_plugin, "default_language"):
            logger.warning(
                "i18n plugin is not configured or missing 'default_language'. Skipping translation."
            )
            return

        if current_language != i18n_plugin.default_language:
            logger.debug(
                f"Skipping on_pre_build hook for language '{current_language}': is not source language '{i18n_plugin.default_language}'"
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
                            translated_content_with_notice = add_translation_notice(
                                content=translated_content,
                                source_lang=source_lang,
                                target_lang=target_lang,
                                theme_name=self.theme_name,
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
