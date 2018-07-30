#!/usr/bin/env python

from aiohttp import web
import aiohttp_jinja2
import jinja2
import aiocoap.resource as resource
import aiocoap

import routes
import resources

import asyncio
import hashlib
import logging
from pathlib import Path
import os.path

PROJECT_ROOT = '.'


def get_binaries():
    p = Path('./uploads/bin')
    binaries = []
    for child in p.iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            binaries.append(resources.ResourceFile(child, url, m))
    return binaries

def get_manifests():
    p = Path('./uploads/man')
    manifests = []
    for child in p.iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            manifests.append(resources.ResourceFile(child, url, m))
    return manifests

def get_public_keys():
    p = Path('./uploads/pk')
    public_keys = []
    for child in p.iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            public_keys.append(resources.ResourceFile(child, url, m))
    return public_keys

@asyncio.coroutine
def init(loop, app):
    srv = yield from loop.create_server(app.make_handler(),
                                        'localhost', 4000)
    return srv


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    loop = asyncio.get_event_loop()

    coap = resource.Site()
    coap.add_resource(('.well-known', 'core'),
                      resource.WKCResource(coap.get_resources_as_linkheader))

    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))

    app['binaries'] = get_binaries()
    app['public_keys'] = get_public_keys()
    app['manifests'] = get_manifests()

    app['coap'] = coap

    for dpt in app['binaries']:
        resources.add_file_resource(coap, dpt)
    for dpt in app['public_keys']:
        resources.add_file_resource(coap, dpt)
    for dpt in app['manifests']:
        resources.add_file_resource(coap, dpt)

    routes.setup_routes(app, PROJECT_ROOT)

    asyncio.Task(aiocoap.Context.create_server_context(coap))
    loop.run_until_complete(init(loop, app))
    print("starting loop!")
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
