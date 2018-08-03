#!/usr/bin/env python

import argparse
import base64
import binascii
import calendar
import cbor
import hashlib
import os
import os.path
import time
import uuid

import ed25519
from pyasn1.type import univ
from pyasn1.type.namedtype import NamedType, NamedTypes
from pyasn1.codec.der.decoder import decode as der_decoder

TEXT_MANIFEST_DESC = 1
TEXT_PAYLOAD_DESC = 2
TEXT_VENDOR = 3
TEXT_MODEL = 4

CONDITION_VENDORID = 1
CONDITION_CLASSID = 2
CONDITION_DEVICEID = 3
CONDITION_BESTBEFORE = 4

DIRECTIVE_APPLY_IMMEDIATE = 1
DIRECTIVE_APPLY_AFTER = 2

PAYLOADFORMAT_BIN = 1
PAYLOADFORMAT_HEX = 2

DIGEST_TYPE_SHA256 = 1
DIGEST_TYPE_SHA384 = 2
DIGEST_TYPE_SHA512 = 3

PAYLOAD_DIGEST_RAW = 1
PAYLOAD_DIGEST_INSTALLED = 2
PAYLOAD_DIGEST_CIPHER = 3
PAYLOAD_DIGEST_PREIMAGE = 4

ASN1_ED25519_TYPE = '1.3.101.112'

def _get_conditions(args):
    conds = []
    uuid_vendor = None
    if args.vendorname:
        uuid_vendor = uuid.uuid5(uuid.NAMESPACE_DNS, str(args.vendorname))
        print("Vendor ID: {}".format(uuid_vendor.hex))
        conds.append([CONDITION_VENDORID, uuid_vendor.bytes])
        if args.classname:
            uuid_class = uuid.uuid5(uuid_vendor, args.classname)
            conds.append([CONDITION_CLASSID, uuid_class.bytes])
            print("Class ID: {}".format(uuid_class.hex))
            if args.deviceid:
                conds.append([CONDITION_DEVICEID,
                              binascii.unhexlify(args.deviceid)])
    if args.valid_duration:

        timestamp = cbor.dumps(cbor.Tag(1, _get_timestamp() + args.valid_duration))
        conds.append([CONDITION_BESTBEFORE, timestamp])
    return conds


def _get_payloadinfo(args):
    return [
             [PAYLOADFORMAT_BIN],
             _get_bin_size(args.filename),
             None,
             [[1, args.uri]],
             [DIGEST_TYPE_SHA256],
             {1: _get_bin_hash(args.filename)},
             None
        ]


def _format_suit(args):
    suit = [
            args.version,
            None,
            _get_nonce(),
            _get_timestamp(),
            _get_conditions(args),
            None,
            None,
            None,
            None,
           ]
    payloadinfo = _get_payloadinfo(args)
    suit.append(payloadinfo)
    return suit


def _get_timestamp():
    return calendar.timegm(time.gmtime())


def _get_nonce():
    return os.urandom(8)


def _get_bin_size(filename):
    return os.path.getsize(filename)


def _get_bin_hash(filename):
    digest = None
    with open(filename, 'rb') as f:
        digest = hashlib.sha256(f.read()).digest()
    return digest


def main(binary, version):
    
    uri = "coap://[2002:8d16:1b8e:28:141:22:28:91]/" + binary.url
    filename = str(binary.path)

    suit = [
            version,
            None,
            _get_nonce(),
            _get_timestamp(),
            None,
            None,
            None,
            None,
            None,
           ]

    payloadinfo = [
             [PAYLOADFORMAT_BIN],
             _get_bin_size(filename),
             None,
             [[1, uri]],
             [DIGEST_TYPE_SHA256],
             {1: _get_bin_hash(filename)},
             None
        ]

    suit.append(payloadinfo)

    return cbor.dumps(suit)

if __name__ == "__main__":
    main()
