import resources
#import gen_unsigned_manifest
import base64

from aiohttp import web
import aiocoap
import aiohttp_jinja2
from multidict import MultiDict
from subprocess import Popen, PIPE, STDOUT
import subprocess
import sys
from common.BuildResult import get_build_result_template
import build_example as b
import ast
from subprocess import call, Popen
import os

import json
from requests.http_prints import print_signed_result, print_bad_request
import logging

#CUR_DIR = os.path.abspath(os.path.dirname(__file__))
#PROJECT_ROOT_DIR = os.path.normpath(os.path.join(CUR_DIR, os.pardir))
#sys.path.append(PROJECT_ROOT_DIR)


async def app_index(request):
    response = aiohttp_jinja2.render_template('app.jinja2',
                                          request,
                                          {'app_approved':request.app['app_approved']})
    return response

async def user_index(request):
    response = aiohttp_jinja2.render_template('user.jinja2',
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
    
async def flash_device(request):


    build_result = b.build('samr21-xpro', 'suit_updater', False, False)
    build_result['output_archive'] = build_result['output_archive'].decode('ascii')


    data = print_signed_result(json.dumps(build_result).encode("ascii"))

    hdrs = MultiDict({'Content-Type': 'application/json',
        'Content-Disposition': 'Attachment;filename=built_archive.json'})
    return web.Response(headers=hdrs,
                        body=data)


async def get_manifest(request):
    version = 2

    #manifest = gen_unsigned_manifest.main(request.app['dyn_resources']['builds'][0],  version)
    mf_gen_dir = "/app2/suit-manifest-generator"
    #os.chdir(mf_gen_dir)
    ##rtn = call("python3 " + mf_gen_dir + "/encode.py " + mf_gen_dir + "/test1.json " +
    ##        mf_gen_dir + "/test-out.cbor", shell=True)
    #rtn = call("python3 ./encode.py ./test1.json ./test-out.cbor", shell=True)
    
    process = Popen("python3 ./encode.py ./test1.json ./test-out.cbor", shell=True,
            cwd=mf_gen_dir)
    process.communicate() #wait for file to be created

    #logging.debug("return code from manifest gen: {}".format(rtn))

    with open("{}/test-out.cbor".format(mf_gen_dir), 'rb') as mf_file:
        manifest = mf_file.read()
    manifest_base64 = base64.b64encode(manifest)

    hdrs = MultiDict({'Content-Disposition':
                      'Attachment;filename=my_manifest.cbor'})

    return web.Response(headers=hdrs,
                        body=manifest_base64)

 
async def upload_signed_manifest(request):
    data = await request.post()
    fw_data = data['signed_manifest']
    fw_file = fw_data.file
    print(type(fw_data))
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
    with request.app['dyn_resources']['signed_manifests'][-1].path.open('rb') as f:
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
