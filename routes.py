import views
import gen_manifest

import os.path


def setup_routes(app, root):
    app.router.add_get('/', views.index)
    app.router.add_get('/files', views.files)
    app.router.add_post('/public_keys', views.public_key_upload)
    app.router.add_post('/binaries', views.binary_upload)
    app.router.add_post('/upload_manifest', views.signed_manifest_upload)
    #app.router.add_post('/gen_manifest', gen_manifest.generate)
    #app.router.add_post('/coap_push', views.coap_push)
    app.router.add_get('/f/{digest}', views.file_by_digest)
    app.router.add_static('/f/bin', path=os.path.join(root, 'uploads/bin'), name='f.bin')
    app.router.add_static('/f/man', path=os.path.join(root, 'uploads/man'), name='f.man')
    app.router.add_static('/f/pk', path=os.path.join(root, 'uploads/pk'), name='f.pk')
