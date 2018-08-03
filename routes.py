import views

import os.path


def setup_routes(app, root):
    app.router.add_get('/', views.index)
    app.
    app.router.add_post('/binaries', views.binary_upload)
    app.router.add_post('/upload_manifest', views.signed_manifest_upload)
    app.router.add_post('/get_manifest', views.get_manifest)
    app.router.add_post('/coap_push', views.coap_push)
    app.router.add_static('/static', path=os.path.join(root,'static'), name='static')
