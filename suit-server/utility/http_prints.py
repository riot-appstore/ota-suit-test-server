#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
 * Copyright (C) 2018 FU Berlin
 *
 * This file is subject to the terms and conditions of the GNU Lesser
 * General Public License v2.1. See the file LICENSE in the top level
 * directory for more details.
"""

from __future__ import absolute_import, print_function, unicode_literals

import json
import sys
import os

from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
from base64 import b64encode

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_DIR = os.path.abspath(os.path.join(__file__, "../../.."))
PRIVATE_KEY_FILE = os.path.join(PROJECT_ROOT_DIR, 'website.pem')


class _HttpStatus(object):
    """class to represent HTTP status"""

    code = None
    description = None

    def __init__(self, status_code, description):
        self.status_code = status_code
        self.description = 'Status: {} {}'.format(status_code, description)

    def __str__(self):
        return self.description


_HTTP_OK = _HttpStatus(200, 'OK')
_HTTP_BAD_REQUEST = _HttpStatus(400, 'Bad Request')
_HTTP_UNAUTHORIZED = _HttpStatus(401, 'Unauthorized')
_HTTP_INTERNAL_SERVER_ERROR = _HttpStatus(500, 'Internal Server Error')


def print_signed_result(content):
    """like print_result, but also signing the message by putting message and signature in to two json fields"""

    def get_signature(private_key, message):

        key = open(private_key, 'r').read()

        rsa_key = RSA.importKey(key)
        signer = PKCS1_v1_5.new(rsa_key)
        digest = SHA256.new()

        digest.update(message)
        signature = signer.sign(digest)

        return signature

    signature = get_signature(PRIVATE_KEY_FILE, content)

    signed_message = {
        'message': content,
        'signature': b64encode(signature),
    }
    #Added for python3
    signed_message['message'] = signed_message['message'].decode("ascii")
    signed_message['signature'] = signed_message['signature'].decode("ascii")
    return json.dumps(signed_message)

    #__print_with_http_status__(_HTTP_OK, json.dumps(signed_message))


def print_result(content):
    __print_with_http_status__(_HTTP_OK, content)


def print_bad_request(content):
    __print_with_http_status__(_HTTP_BAD_REQUEST, content)
    sys.exit()


def print_unauthorized(content):
    __print_with_http_status__(_HTTP_UNAUTHORIZED, content)
    sys.exit()


def print_internal_server_error(content):
    __print_with_http_status__(_HTTP_INTERNAL_SERVER_ERROR, content)
    sys.exit()


def __print_with_http_status__(http_status, content):

    print('Content-Type: application/json')

    print(http_status)

    print('\n\r')
    print(content)
