# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import json
import requests
import logging


def translate_with_simpleen(
    config, content, source_lang, target_lang, logger: logging.Logger
):
    """Translate content using Simpleen API"""
    logger.warning("Simpleen translation service is untestet.")

    translated_text = None

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
    except requests.exceptions.RequestException as e:
        raise Exception(f"Simpleen API request failed: {str(e)}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON response: {str(e)}")
    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")

    return translated_text
