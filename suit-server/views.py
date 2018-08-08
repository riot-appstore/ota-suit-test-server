import resources
import gen_unsigned_manifest

from aiohttp import web
import aiocoap
import aiohttp_jinja2
from multidict import MultiDict
import sys

import logging


async def index(request):
    response = aiohttp_jinja2.render_template('files.jinja2',
                                          request,
                                          {'app_approved':request.app['app_approved']})
    return response

async def download_keygen(request):
    print(request.app['dyn_resources']['keygens'])
    with request.app['dyn_resources']['keygens'][0].path.open('rb') as f:
        data = f.read()
    hdrs = MultiDict({'Content-Disposition':
                      'Attachment;filename={}'.format(request.app['dyn_resources']['keygens'][0].path.name)})
    return web.Response(headers=hdrs,
                        body=data)


async def upload_publickey(request):
    data = await request.post()
    print(data)
    pk_data = data['public_key']
    pk = pk_data.file
    logging.debug("uploaded file {}".format(pk_data.filename))
    content = pk.read()
    res = resources.add_upload("public_key", request.app['dyn_resources']['public_keys'],
                              request.app['coap'],
                              pk_data.filename, content)
    if not res:
        raise web.HTTPUnprocessableEntity
    return web.Response(text='{} with digest {} stored'.format(res.path.name,
                                                               res.digest))
    
async def download_flasher(request):
    with request.app['dyn_resources']['flasher_paks'][0].path.open('rb') as f:
        data = f.read()
    hdrs = MultiDict({'Content-Disposition':
                      'Attachment;filename={}'.format(request.app['dyn_resources']['flasher_paks'][0].path.name)})
    return web.Response(headers=hdrs,
                        body=data)


async def get_manifest(request):
    data = await request.post()
    version = 2

    manifest = gen_unsigned_manifest.main(request.app['dyn_resources']['builds'][0],  version)

    hdrs = MultiDict({'Content-Disposition':
                      'Attachment;filename=my_manifest.cbor'})
    return web.Response(headers=hdrs,
                        body=manifest)

 
async def upload_signed_manifest(request):
    data = await request.post()
    fw_data = data['signed_manifest']
    fw_file = fw_data.file
    logging.debug("upload on file {}".format(fw_data.filename))
    content = fw_file.read()
    fw = resources.add_upload("signed_manifest", request.app['dyn_resources']['signed_manifests'],
                              request.app['coap'],
                              fw_data.filename, content)

    print(fw)
    request.app['app_approved'] = "true"

    if not fw:
        request.app['app_approved'] = "false"
        raise web.HTTPUnprocessableEntity
    return web.Response(text='{} with digest {} stored'.format(fw.path.name,
                                                               fw.digest))


async def ota_deploy(request):
    data = await request.post()
    target = data['target']
    logging.info("CoAP send requested uploaded manifest to {}".format(target))
    with request.app['dyn_resources']['signed_manifests'][0].path.open('rb') as f:
        content = f.read()

    protocol = await aiocoap.Context.create_client_context()
    deployrequest = aiocoap.Message(code=aiocoap.POST, uri=target, payload=content)
    try:
        await protocol.request(deployrequest).response
    except Exception as e:
        logging.warning("Error sending coap request: ".format(e))
        return web.Response(text="Error sending file {}"
                                 " to target {}".format(request.app['dyn_resources']['signed_manifests'][0].path.name,
                                                        target))
    return web.Response(text="Sent file {} to target {}".format(request.app['dyn_resources']['signed_manifests'][0].path.name,
                                                                target))
