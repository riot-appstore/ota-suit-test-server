#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2017 Hendrik van Essen
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

from __future__ import print_function

import argparse
import logging
import os
import sys
import time
from shutil import copytree, rmtree, copyfile
import pprint
from utility import config
from utility import build_utility as b_util

# append root of the python code tree to sys.apth so that imports are working
#   alternative: add path to rapstore_backend to the PYTHONPATH environment variable, but this includes one more step
#   which could be forget
CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.abspath(os.path.join(__file__, "../../../.."))
sys.path.append(PROJECT_ROOT_DIR)

LOGFILE = os.path.join(CUR_DIR, 'log', 'build_example.log')
LOGFILE = os.environ.get('BACKEND_LOGFILE', LOGFILE)

APPLICATION_CACHE_DIR = os.path.join(PROJECT_ROOT_DIR, config.APPLICATION_CACHE_DIR)


def _replace_application_name(path, application_name):
    """
    Replace application name in line which starts with "APPLICATION="

    Parameters
    ----------
    path: string
        Path to the file

    application_name: string
        Name of the application

    """

    # Save the old one to check later in case there is an error
    copyfile(path, path + '.old')

    with open(path + '.old', 'r') as old_makefile:
        with open(path, 'w') as makefile:

            for line in old_makefile.readlines():
                if line.replace(' ', '').startswith('APPLICATION='):
                    line = 'APPLICATION = %s\n' % application_name

                makefile.write(line)


def build(board, source_app_name, using_cache, prefetching): 

    build_result = b_util.get_build_result_template()

    app_path = os.path.join(PROJECT_ROOT_DIR, 'RIOT/examples',
            source_app_name)

    build_result['board'] = board

    app_build_parent_dir = os.path.join(PROJECT_ROOT_DIR, 'RIOT',
            'examples_rapstorebuilds')

    # unique application directory name
    ticket_id = b_util.get_ticket_id()

    app_name = 'application%s' % ticket_id
    app_build_dir = os.path.join(app_build_parent_dir, app_name)

    temp_dir = b_util.get_temporary_directory(PROJECT_ROOT_DIR, ticket_id)
    b_util.create_directories(temp_dir)

    build_result['application_name'] = app_name

    # copy application from examples/ to examples_rapstorebuilds/
    copytree(app_path, app_build_dir)

    app_build_dir_abs_path = os.path.abspath(app_build_dir)
    bin_dir = b_util.get_bindir(app_build_dir_abs_path, board)

    # replace name of application in build application's makefile
    _replace_application_name(os.path.join(app_build_dir, 'Makefile'), app_name)
    before = time.time()

    build_result['cmd_output'] += b_util.execute_makefile(app_build_dir,
            board, app_name, '$(date +%s)')

    logging.debug('Build time: %f', time.time() - before)

    # Strip and zip the repo
    try:
        stripped_repo_path = b_util.generate_stripped_repo(app_build_dir, PROJECT_ROOT_DIR, temp_dir, board, app_name)

        archive_path = os.path.join(temp_dir, 'RIOT_stripped.tar')
        before = time.time()
        b_util.zip_repo(stripped_repo_path, archive_path)
        logging.debug('Create archive time: %f', time.time() - before)

        archive_extension = 'tar'

        build_result['output_archive_extension'] = archive_extension
        build_result['output_archive'] = b_util.file_as_base64(archive_path)

        build_result['success'] = True

    except Exception as e:
        logging.error(str(e), exc_info=True)
        build_result['cmd_output'] += '********Build failure*********'

    # delete temporary directories after finished build
    try:
        rmtree(app_build_dir)
        rmtree(temp_dir)
        return build_result

    except Exception as e:
        logging.error(str(e), exc_info=True)
