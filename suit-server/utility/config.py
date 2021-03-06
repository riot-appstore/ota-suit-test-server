#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

db_config = {
    "host": "localhost",
    "user": "rapstore_backend",
    "passwd": "PASSWORD_BACKEND",
    "db": "riot_os"
}

path_root = "RIOT/"

module_directories = [
    "sys",
    "pkg",
    "drivers"
]

application_directories = [
    "examples"
]

LOGGING_FORMAT = "[%(levelname)s]: %(asctime)s\n"\
                 + "in %(filename)s in %(funcName)s on line %(lineno)d\n"\
                 + "%(message)s\n\n"

APPLICATION_CACHE_DIR = ".application_cache"
