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
import netifaces

PROJECT_ROOT = '.'


def _get_dyn_resources():
    p = Path('../ota-resources/')
    public_keys = []
    signed_mans = []
    builds = []
    flasher_paks = []
    keygens = []
    for child in p.joinpath('pubkeys/').iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            print("test")
            public_keys.append(resources.ResourceFile(child, url, m))

    for child in p.joinpath('signed-man').iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            signed_mans.append(resources.ResourceFile(child, url, m))

    for child in p.joinpath('builds').iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            builds.append(resources.ResourceFile(child, url, m))
    
    for child in p.joinpath('flasher-pak').iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            flasher_paks.append(resources.ResourceFile(child, url, m))

    for child in p.joinpath('keygen').iterdir():
        with child.open('rb') as f:
            m = hashlib.sha1(f.read()).hexdigest()[:16]
            url = os.path.join('f', m)
            keygens.append(resources.ResourceFile(child, url, m))

    resourcedict = {"public_keys": public_keys,
            "signed_manifests": signed_mans,
            "builds": builds,
            "flasher_paks": flasher_paks,
            "keygens": keygens}
    return resourcedict



@asyncio.coroutine
def init(loop, app):
    srv = yield from loop.create_server(app.make_handler(),
                                        '0.0.0.0', 8080)
				       #'localhost', 80)
    return srv


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    loop = asyncio.get_event_loop()

    coap = resource.Site()
    coap.add_resource(('.well-known', 'core'),
                      resource.WKCResource(coap.get_resources_as_linkheader))


    app = web.Application(loop=loop)
    aiohttp_jinja2.setup(app,
                         loader=jinja2.FileSystemLoader('templates'))

    app['dyn_resources'] = _get_dyn_resources()
    
    app['app_approved'] = "false"
    
    app['coap'] = coap
    app['static_root_url'] = './static'

    for dpt in app['dyn_resources']['public_keys']:
        resources.add_file_resource(coap, dpt)
    for dpt in app['dyn_resources']['signed_manifests']:
        resources.add_file_resource(coap, dpt)
    for dpt in app['dyn_resources']['builds']:
        resources.add_file_resource(coap, dpt)
    for dpt in app['dyn_resources']['flasher_paks']:
        resources.add_file_resource(coap, dpt)
    for dpt in app['dyn_resources']['keygens']:
        resources.add_file_resource(coap, dpt)

    routes.setup_routes(app, PROJECT_ROOT)

    asyncio.Task(aiocoap.Context.create_server_context(coap))
    loop.run_until_complete(init(loop, app))

    print("Server started")
    addrs = netifaces.ifaddresses('eth0')
    #addrs = netifaces.ifaddresses('wlp4s0')
    ipv6_add = addrs[netifaces.AF_INET6][0]['addr']
    logging.debug("Server IPv6 address is: {}".format(ipv6_add))
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
