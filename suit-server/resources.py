import aiocoap
import aiocoap.resource as resource
from collections import namedtuple
import hashlib
import os.path
from pathlib import Path
import logging


def check_exists(uploads, name, digest):
    for upload in uploads:
        if upload.digest == digest:
            return True
      #  if upload.path.name == name:
      #      return True
    return False


def add_upload(resourcetype, uploads, coap, name, content):
    resourcedir = '../ota-resources/'
    m = hashlib.sha1(content).hexdigest()[:16]
    if check_exists(uploads, name, m):
        return None

    if resourcetype == "signed_manifest":
        logging.debug("uploading signed manifest")
        with open(os.path.join(resourcedir, 'signed-man', name), 'wb') as f:
            f.write(content)
            logging.debug("content is {}".format(content))
        res = ResourceFile(Path(os.path.join(resourcedir, 'signed-man', name)),
                          os.path.join('/f/man', m), m)
        logging.debug("res is {}".format(res))

    if resourcetype == "public_key":
        with open(os.path.join(resourcedir, 'pubkeys', name), 'wb') as f:
            f.write(content)
        res = ResourceFile(Path(os.path.join(resourcedir, 'pubkeys', name)),
                          os.path.join('/f/pk', m), m)
        
    add_file_resource(coap, res)
    uploads.append(res)
    return res


def add_file_resource(coap, fw):
    print("added resource from " + str(fw.path))
    print("added resource at " + str(fw.url))
    print("digest of resource is " + str(fw.digest))
    coap.add_resource(('f', fw.digest),
                      FileResource(fw.path))


class ResourceFile(namedtuple('ResourceFile', ['path', 'url', 'digest'])):
        pass


class FileResource(resource.Resource):

    def __init__(self, path):
        super().__init__()
        self.path = path

    async def render_get(self, request):
        content = b""
        with self.path.open('rb') as f:
            content = f.read()
        return aiocoap.Message(payload=content)
