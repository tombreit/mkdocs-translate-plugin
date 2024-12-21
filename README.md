<!--
SPDX-FileCopyrightText: 2024 Thomas Breitner

SPDX-License-Identifier: MIT
-->

# mkdocs-translate-plugin

Wrote something in MkDocs and realised that nobody understands it?  
*Maybe a translation would help.*

Don't feel like translating?  
*Let this plugin do it for you.*

**🔥 This is work in progress - no liability for nothing.**

## Features

- Translates the markdown files in your MkDocs project from your primary language into your desired target languages
- Processes `.md` files
- Supports **DeepL**, **Academiccloud.de / LLama** and **Simpleen**
- Creates a translation only if it does not yet exist
- Tries - and often fails - to preserve the original markdown formatting. If you have any idea how I can improve this, please let me know.
- tbc

## Install

*Currently only available via it's git repository.*

```bash
# Initial install:
python -m pip install 'mkdocs-translate-plugin @ git+https://github.com/tombreit/mkdocs-translate-plugin'

# Upgrade plugin:
python -m pip install --upgrade --no-deps --force-reinstall 'mkdocs-translate-plugin @ git+https://github.com/tombreit/mkdocs-translate-plugin'
```

This should install some requirements. See [`pyproject.toml`](https://github.com/tombreit/mkdocs-translate-plugin/blob/main/pyproject.toml) for details.

## Configuration

- Activate the `i18n` plugin
- Set the languages for your project in [`mkdocs.yml`](https://github.com/tombreit/mkdocs-translate-plugin/blob/main/mkdocs.yml)
- Your primary/source language markdown files must be named like `<filename>.<languagecode>.md`, eg: `setup.en.md`
- Set the translation service in `mkdocs.yml`
- Provide the API key as an environment variable, eg: `export TRANSLATION_SERVICE_API_KEY=secret`
