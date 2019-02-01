import resources
import gen_unsigned_manifest

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

#    board = "samr21-xpro"
#
#    build_result = get_build_result_template()
#    build_result['board'] = board
#    app_build_parent_dir = os.path.join('/', 'RIOT', 'generated_by_rapstore')
#    ticket_id = b_util.get_ticket_id()
#    app_name = 'application%s' % ticket_id
#    app_build_dir = os.path.join(app_build_parent_dir, app_name)
#    temp_dir = b_util.get_temporary_directory("/", ticket_id)
#    build_result['application_name'] = app_name
#    b_util.create_directories(app_build_dir)
#
#    # `make` the basic OTA CoAP application using the user's public key
#    build_result['cmd_output'] += b_util.execute_makefile('/RIOT/examples/suit_updater', 'samr21-xpro', 'suit_updater', '$(date +%s)')
#
#    try:
#        stripped_repo_path = b_util.generate_stripped_repo(app_build_dir, PROJECT_ROOT_DIR, temp_dir, board, app_name)
#
#        archive_path = os.path.join(temp_dir, 'RIOT_stripped.tar')
#        b_util.zip_repo(stripped_repo_path, archive_path)
#
#        archive_extension = 'tar'
#
#        build_result['output_archive_extension'] = archive_extension
#        build_result['output_archive'] = b_util.file_as_base64(archive_path)
#
#        build_result['success'] = True
#
#    except Exception as e:
#        logging.error(str(e), exc_info=True)
#        build_result['cmd_output'] += 'something went wrong on server side'
#
#    # delete temporary directories after finished build
#    try:
#        rmtree(app_build_dir)
#        rmtree(temp_dir)
#
#    except Exception as e:
#        logging.error(str(e), exc_info=True)
    # cut down the RIOT repo

    # zip the file

    # send to the browser extention for flashing

    build_result = b.build('samr21-xpro', 'suit_updater', False, False)
    # This now makes it parseable by json.dumps 
    # I'm now having trouble getting the public key "website.pem" to be
    # imported in the right format and therefore processed without errors  
    # I think this is because my "website.pem" is the whole webpage, not just
    # the key...
    build_result['output_archive'] = build_result['output_archive'].decode('ascii')

   # cmd = ['python3', 'build_example.py',
   #        '--application', 'suit_updater',
   #        '--board', 'samr21-xpro']#,
   #        #'--caching']

   # output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd='./').strip()

   # # convert string representation of dictionary to "real" dictionary
   # build_result = ast.literal_eval(output)
   # build_result['cmd_output'] = build_result['cmd_output'].replace('\n', '<br>')

   # print_signed_result(json.dumps(build_result))

    data = print_signed_result(json.dumps(build_result).encode("ascii"))

    #with request.app['dyn_resources']['flasher_paks'][0].path.open('rb') as f:
    #    data = f.read()
    #hdrs = MultiDict({'Content-Disposition':
    #                  'Attachment;filename={}'.format(request.app['dyn_resources']['flasher_paks'][0].path.name)})
    hdrs = MultiDict({'Content-Type': 'application/json',
        'Content-Disposition': 'Attachment;filename=built_archive.json'})
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
