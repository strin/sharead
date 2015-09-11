#import shareread.storage.dropbox as store
import shareread.storage.local as store
from shareread.server.utils import parse_webkitform
from tornado import (ioloop, web)
import md5
import base64
from StringIO import StringIO

class UploadHandler(web.RequestHandler):
    def get(self):
        self.render("upload.html")

class UploadSubmitHandler(web.RequestHandler):
    def post(self):
        form = parse_webkitform(self.request.body)
        # get data.
        data = form['data']
        data_stream = StringIO(data)
        # get filehash.
        md5_code = md5.new()
        md5_code.update(data)
        filehash = base64.b64encode(md5_code.digest())
        store.put_file(store.TEST_ACCESS_TOKEN, filehash, data_stream)

handlers = [
    (r"/img/(.*)", web.StaticFileHandler, {"path": "frontend/static/img/"}),
    (r"/css/(.*)", web.StaticFileHandler, {"path": "frontend/static/css/"}),
    (r"/js/(.*)", web.StaticFileHandler, {"path": "frontend/static/js/"}),
    (r"/upload", UploadHandler),
    (r"/upload-submit", UploadSubmitHandler)
]

settings = {
    "autoreload": True,
    "debug": True,
    "template_path": "frontend/template/"
}


if __name__ == "__main__":
    application = web.Application(handlers, **settings)
    application.listen(8888, address="0.0.0.0")
    ioloop.IOLoop.current().start()


