#import shareread.storage.dropbox as store
import shareread.storage.local as store
from shareread.server.utils import (parse_webkitform, parse_filename)
from shareread.server.db import update_file_entry
from tornado import (ioloop, web)
import md5
import base64
import json
from StringIO import StringIO

class UploadHandler(web.RequestHandler):
    def get(self):
        self.render("upload.html")

class UploadSubmitHandler(web.RequestHandler):
    def post(self):
        form = parse_webkitform(self.request.body)
        # get filename.
        (filename, ext) = parse_filename(form['filename'])
        # get data.
        data = form['data']
        data_stream = StringIO(data)
        # get filehash.
        md5_code = md5.new()
        md5_code.update(data)
        filehash = base64.b64encode(md5_code.digest())
        filehash = '.'.join([filehash, ext])
        store.put_file(store.TEST_ACCESS_TOKEN, filehash, data_stream)
        # update db.
        update_file_entry(filehash, filename)
        self.write({
            'filehash':filehash,
            'response':'OK'
        })

class FileUpdateHandler(web.RequestHandler):
    def post(self):
        filehash = json.loads(self.get_argument('filehash'))
        filename = json.loads(self.get_argument('filename'))
        # update db.
        update_file_entry(filehash, filename)
        self.write({
            'response':'OK'
        })

handlers = [
    (r"/img/(.*)", web.StaticFileHandler, {"path": "frontend/static/img/"}),
    (r"/css/(.*)", web.StaticFileHandler, {"path": "frontend/static/css/"}),
    (r"/js/(.*)", web.StaticFileHandler, {"path": "frontend/static/js/"}),
    (r"/mustache/(.*)", web.StaticFileHandler, {"path": "frontend/static/mustache/"}),
    (r"/upload", UploadHandler),
    (r"/upload-submit", UploadSubmitHandler),
    (r"/file/update", FileUpdateHandler)
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


