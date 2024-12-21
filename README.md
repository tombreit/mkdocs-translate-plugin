<!--
SPDX-FileCopyrightText: 2024 Thomas Breitner

SPDX-License-Identifier: MIT
-->

# mkdocs-translate-plugin

Wrote something in MkDocs and realised that nobody understands it?  
*Maybe a translation would help.*

Don't feel like translating?  
*Let this plugin do it for you.*

I don't get it: What does this plugin do?  
*This plugin does the same as if you had hired someone to translate your markdown files: find the original markdown file, translate the content - possibly into several languages - create translation file(s) with the correct file name and save the translated markdown content to that file.*  
*The actual translation is done by one of the configured (external) translation services.*  
*This plugin does its work before MkDocs starts converting the markdown files to HTML files. You can therefore easily view and edit the results of this plugin locally via `mkdocs serve`.*  
*To be fair: If you hire a translater with some markdown knowledge, you could get better results.*

**🔥 This is work in progress - no liability for nothing.**

## Features

- Translates the markdown files in your MkDocs project from your primary language into your desired target languages
- Processes `.md` files, eg:  `<filename>.en.md` → `<filename>.<language>.md`
- Supports **DeepL**, **Academiccloud.de / LLama** and **Simpleen**
- Creates a translation only if it does not yet exist
- Tries - and often fails - to preserve the original markdown formatting. If you have any idea how I can improve this, please let me know.
- Runs only on the MkDocs `build` command so as not to waste your translation provider/service API contingent
- Get some verbose info by running `mkdocs --verbose build`
- tbc

## Install

*Currently only available via it's git repository.*

```bash
# Initial install:
python -m pip install \
  'mkdocs-translate-plugin @ git+https://github.com/tombreit/mkdocs-translate-plugin'

# Upgrade plugin:
python -m pip install \
  --upgrade --no-deps --force-reinstall \
  'mkdocs-translate-plugin @ git+https://github.com/tombreit/mkdocs-translate-plugin'
```

This should install some requirements. See [`pyproject.toml`](https://github.com/tombreit/mkdocs-translate-plugin/blob/main/pyproject.toml) for details.

## Configuration

- Activate the `i18n` plugin
- Set the languages for your project in [`mkdocs.yml`](https://github.com/tombreit/mkdocs-translate-plugin/blob/main/mkdocs.yml)
- Your primary/source language markdown files must be named like `<filename>.<languagecode>.md`, eg: `setup.en.md`
- Set the translation service in `mkdocs.yml`
- Provide the API key as an environment variable, eg: `export TRANSLATION_SERVICE_API_KEY=secret`

## Behind the scenes

- Uses - obviously - [MkDocs](https://www.mkdocs.org/)
- Uses [mkdocs-static-i18n](https://ultrabug.github.io/mkdocs-static-i18n/) to "compile" different languages
- Uses [mkdocs-material](https://squidfunk.github.io/mkdocs-material/) to provide a theme with a language switcher

## Try it

1. Setup plugin and demo project locally

    ```bash
    git clone git@github.com:tombreit/mkdocs-translate-plugin.git
    cd mkdocs-translate-plugin
    python3 -m venv .venv
    source .venv/bin/activate
    pip install  --editable .
    ```

1. Get an API key for a supported translation provider:
    - [Simpleen (Free Plan) API key](https://simpleen.io/signup)
    - [DeepL API](https://www.deepl.com/en/pro#developer)
    - [Academic Cloud AI chatbot](https://academiccloud.de/services/chatai/)

1. Export the API key as an environment variable and set corresponding translation provider (see Configuration section above)

1. Validate current EN-only docs

    ```bash
    $ tree docs/
    docs/
    ├── index.en.md
    └── uptimekuma.en.md
    
    1 directory, 2 files
    ```

1. Let this plugin do it's work

    ```bash
    mkdocs build
    ```

1. Validate created translations exists

    ```bash
    $ tree docs/
    docs/
    ├── index.de.md
    ├── index.en.md
    ├── uptimekuma.de.md
    └── uptimekuma.en.md
    
    1 directory, 4 files
    ```

1. Enjoy your translated MkDocs project

    ```bash
    mkdocs serve
    ```
