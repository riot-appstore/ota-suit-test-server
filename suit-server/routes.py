import views

import os.path


def setup_routes(app, root):
    app.router.add_get('/app', views.app_index)
    app.router.add_get('/user', views.user_index)
    app.router.add_get('/download_keygen', views.download_keygen)
    app.router.add_post('/upload_publickey', views.upload_publickey)
    app.router.add_get('/flash_device', views.flash_device)
    app.router.add_get('/get_manifest', views.get_manifest)
    app.router.add_post('/upload_signed_manifest', views.upload_signed_manifest)
    app.router.add_post('/ota_deploy', views.ota_deploy)
    app.router.add_static('/static', path=os.path.join(root,'static'), name='static')
