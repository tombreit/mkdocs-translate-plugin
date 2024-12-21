# SPDX-FileCopyrightText: 2024 Thomas Breitner
#
# SPDX-License-Identifier: MIT

"""
MkDocs Translate Plugin
"""

from pathlib import Path
from typing import Literal

import mkdocs

from .translation_services import translate_content


log = mkdocs.plugins.get_plugin_logger(__name__)


class TranslatePluginConfig(mkdocs.config.base.Config):
    translation_service = mkdocs.config.config_options.Choice(
        choices=["simpleen", "deepl", "openai"]
    )
    translation_service_api_key = mkdocs.config.config_options.Type(str)


class TranslatePlugin(mkdocs.plugins.BasePlugin[TranslatePluginConfig]):
    def __init__(self):
        self.is_serve = False

    def on_startup(
        self, *, command: Literal["build", "gh-deploy", "serve"], dirty: bool
    ) -> None:
        self.is_serve = command == "serve"

    def on_pre_build(self, config):
        """Translate files before build process starts"""

        if self.is_serve:
            log.info("Plugin deactivated during `serve`. Only active during `build`.")
            return

        # Current run language. The mkdocs-static-i18n processes the
        # on_pre_build hook for each language, but we only neet to
        # trigger the translation for the default source language.
        i18n_plugin = config.plugins.get("i18n")
        current_language = config.theme.get("language")

        if current_language != i18n_plugin.default_language:
            log.debug(
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
                log.info(
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

                    if target_filepath.exists():
                        log.info(
                            f"Translation file already exists: {target_filepath.name}. Skipping..."
                        )
                    else:
                        log.info(
                            f"[🔥] Translating {rel_filepath.name} to {target_filepath.name}..."
                        )
                        source_content = filepath.read_text(encoding="utf-8")
                        translated_content = translate_content(
                            config=self.config,
                            content=source_content,
                            source_lang=i18n_plugin.default_language,
                            target_lang=lang,
                        )

                        if translated_content:
                            new_path = filepath.parent / target_filename
                            new_path.write_text(translated_content, encoding="utf-8")
                        else:
                            log.warning(
                                f"Translation failed for {rel_filepath.name} to {target_filename}"
                            )
