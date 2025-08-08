# SPDX-FileCopyrightText: Thomas Breitner
#
# SPDX-License-Identifier: MIT

import logging


# Create the logger for the entire plugin, no matter in which
# module its used
logger = logging.getLogger("mkdocs_translate_plugin")
logger.setLevel(logging.DEBUG)

# Create a file handler to log to a file
file_handler = logging.FileHandler("mkdocs_translate_plugin.log")
file_handler.setLevel(logging.INFO)

# Create a console handler to log to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Define a log format
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
