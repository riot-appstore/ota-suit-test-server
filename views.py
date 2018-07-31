import resources
import gen_manifest

from aiohttp import web
import aiocoap
import aiohttp_jinja2
from multidict import MultiDict

import logging


async def index(request):
    text = """
    This website is a test server for the SUIT hackathon. Presented here is a
    small file (1MB max) storage for firmware binaries and SUIT manifests.
    Everything is publicly available without any restrictions, so BE CAREFUL
    with what you upload here.

    If you agree with these conditions, please continue to /files for actual
    functionality.
    """
    return web.Response(text=text)


async def files(request):
    response = aiohttp_jinja2.render_template('files.jinja2',
                                          request,
                                          {'binaries': request.app['binaries'],
                                           'public_keys': request.app['public_keys'],
                                           'manifests': request.app['manifests']})
    return response


async def public_key_upload(request):
    data = await request.post()
    fw_data = data['public_key']
    fw_file = fw_data.file
    logging.debug("upload on file {}".format(fw_data.filename))
    content = fw_file.read()
    fw = resources.add_upload_pk(request.app['public_keys'],
                              request.app['coap'],
                              fw_data.filename, content)
    if not fw:
        raise web.HTTPUnprocessableEntity
    return web.Response(text='{} with digest {} stored'.format(fw.path.name,
                                                               fw.digest))


async def binary_upload(request):
    data = await request.post()
    fw_data = data['binary']
    fw_file = fw_data.file
    logging.debug("upload on file {}".format(fw_data.filename))
    content = fw_file.read()
    fw = resources.add_upload_bin(request.app['binaries'],
                              request.app['coap'],
                              fw_data.filename, content)
    if not fw:
        raise web.HTTPUnprocessableEntity
    return web.Response(text='{} with digest {} stored'.format(fw.path.name,
                                                               fw.digest))

async def signed_manifest_upload(request):
    data = await request.post()
    fw_data = data['manifest']
    fw_file = fw_data.file
    logging.debug("upload on file {}".format(fw_data.filename))
    content = fw_file.read()
    fw = resources.add_upload_man(request.app['manifests'],
                              request.app['coap'],
                              fw_data.filename, content)
    if not fw:
        raise web.HTTPUnprocessableEntity
    return web.Response(text='{} with digest {} stored'.format(fw.path.name,
                                                               fw.digest))

async def file_by_digest(request):
    digest = request.match_info['digest']
    binaries = request.app['binaries']
    public_keys = request.app['public_keys']
    manifests = request.app['manifests']
    req_fw = None
    for fw in binaries:
        if fw.digest == digest:
            req_fw = fw
    for fw in public_keys:
        if fw.digest == digest:
            req_fw = fw
    for fw in manifests:
        if fw.digest == digest:
            req_fw = fw
    if not req_fw:
        raise web.HTTPNotFound
    with req_fw.path.open('rb') as f:
        data = f.read()
    hdrs = MultiDict({'Content-Disposition':
                      'Attachment;filename={}'.format(req_fw.path.name)})
    return web.Response(headers=hdrs,
                        body=data)


async def get_manifest(request):
    data = await request.post()
    #public_key = data['public_key']
    binary_dig = data['binary']
    binaries = request.app['binaries']
    req_b = None
    for b in binaries:
        if b.digest == binary_dig:
            req_b = b

    full_url = "coap://[2002:8d16:1b8e:28:141:22:28:91]/" + req_b.url
    print(full_url)

    version = 1

    manifest = gen_manifest.gen_unsigned(req_b,  version)

    hdrs = MultiDict({'Content-Disposition':
                      'Attachment;filename=my_manifest.cbor'})
    return web.Response(headers=hdrs,
                        body=manifest)


#async def coap_push(request):
#    data = await request.post()
#    target = data['target']
#    # sign = True if 'signed' in data else False
#    digest = data['file']
#    fw = None
#    logging.info("CoAP send requested with {} to {}".format(digest, target))
#    for upload in request.app['uploads']:
#        if upload.digest == digest:
#            fw = upload
#    if not fw:
#        raise web.HTTPNotFound
#    with fw.path.open('rb') as f:
#        content = f.read()
#
#    protocol = await aiocoap.Context.create_client_context()
#    request = aiocoap.Message(code=aiocoap.POST, uri=target, payload=content)
#    try:
#        await protocol.request(request).response
#    except Exception as e:
#        logging.warning("Error sending coap request: ".format(e))
#        return web.Response(text="Error sending file {}"
#                                 " to target {}".format(fw.path.name,
#                                                        target))
#    return web.Response(text="Sent file {} to target {}".format(fw.path.name,
#                                                                target))
