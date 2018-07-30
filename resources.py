import aiocoap
import aiocoap.resource as resource
from collections import namedtuple
import hashlib
import os.path
from pathlib import Path


def check_exists(uploads, name, digest):
    for upload in uploads:
        if upload.digest == digest:
            return True
        if upload.path.name == name:
            return True
    return False


def add_upload_bin(uploads, coap, name, content):
    m = hashlib.sha1(content).hexdigest()[:16]
    if check_exists(uploads, name, m):
        return None
    with open(os.path.join('./uploads/bin', name), 'wb') as f:
        f.write(content)
    fw = ResourceFile(Path(os.path.join('uploads/bin', name)),
                      os.path.join('/f/bin', m), m)
    add_file_resource(coap, fw)
    uploads.append(fw)
    return fw

def add_upload_pk(uploads, coap, name, content):
    m = hashlib.sha1(content).hexdigest()[:16]
    if check_exists(uploads, name, m):
        return None
    with open(os.path.join('./uploads/pk', name), 'wb') as f:
        f.write(content)
    fw = ResourceFile(Path(os.path.join('uploads/pk', name)),
                      os.path.join('/f/pk', m), m)
    add_file_resource(coap, fw)
    uploads.append(fw)
    return fw

def add_upload_man(uploads, coap, name, content):
    m = hashlib.sha1(content).hexdigest()[:16]
    if check_exists(uploads, name, m):
        return None
    with open(os.path.join('./uploads/man', name), 'wb') as f:
        f.write(content)
    fw = ResourceFile(Path(os.path.join('uploads/man', name)),
                      os.path.join('/f/man', m), m)
    add_file_resource(coap, fw)
    uploads.append(fw)
    return fw

def add_file_resource(coap, fw):
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
