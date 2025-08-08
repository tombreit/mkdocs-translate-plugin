# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import importlib
import logging


def translate_content(
    config, content: str, source_lang: str, target_lang: str, logger: logging.Logger
) -> str:
    """
    Translate content using the configured service.
    Dynamically imports the corresponding module and calls the translation function.
    """
    module_name = f"mkdocs_translate_plugin.translation_services.{config.translation_service.lower()}"
    function_name = f"translate_with_{config.translation_service.lower()}"

    try:
        module = importlib.import_module(module_name)
        translation_func = getattr(module, function_name)
        return translation_func(config, content, source_lang, target_lang, logger)

    except ModuleNotFoundError:
        logger.error(f"Translation service module '{module_name}' not found.")
        raise ValueError(
            f"Unsupported translation service: {config.translation_service}"
        )

    except AttributeError:
        logger.error(
            f"Translation function '{function_name}' not found in module '{module_name}'."
        )
        raise ValueError(
            f"Unsupported translation service: {config.translation_service}"
        )
