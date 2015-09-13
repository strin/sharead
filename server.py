from tornado import (ioloop, web)
import md5
import base64
import json
from StringIO import StringIO
from datetime import datetime

#import shareread.storage.dropbox as store
import shareread.storage.local as store
from shareread.server.utils import (parse_webkitform, parse_filename,
                                    create_thumbnail, get_thumbnail)
from shareread.server.db import (update_file_entry, add_recent_entry)
from shareread.server.recents import (RECENTS_ADD, RECENTS_UPDATE, fetch_num_activities)

def TemplateRenderHandler(template):
    class UploadHandler(web.RequestHandler):
        def get(self):
            self.render(template)
    return UploadHandler

class UploadSubmitHandler(web.RequestHandler):
    def post(self):
        form = parse_webkitform(self.request.body)
        # get filename.
        (filename, ext) = parse_filename(form['filename'])
        if ext != 'pdf':
            self.set_status(300)
            self.write('only pdfs are supported')
            return
        # get data.
        data = form['data']
        data_stream = StringIO(data)
        # get filehash.
        md5_code = md5.new()
        md5_code.update(data)
        filehash = base64.b64encode(md5_code.digest())
        filehash = '.'.join([filehash, ext])
        store.put_file(store.TEST_ACCESS_TOKEN, filehash, data_stream)
        # get upload date.
        upload_date = str(datetime.now())
        # create thumbnail.
        thumb_path = create_thumbnail(filehash)
        # update db.
        update_file_entry(filehash, filename, ext, upload_date, thumb_path=thumb_path)
        add_recent_entry(filehash, action_type=RECENTS_ADD)
        self.write({
            'filehash':filehash,
            'filename':filename,
            'response':'OK'
        })

class FileUpdateHandler(web.RequestHandler):
    def post(self):
        filehash = json.loads(self.get_argument('filehash'))
        filename = json.loads(self.get_argument('filename'))
        # update db.
        update_file_entry(filehash, filename)
        add_recent_entry(filehash, action_type=RECENTS_UPDATE)
        self.write({
            'response':'OK'
        })

class RecentItemsHandler(web.RequestHandler):
    def get(self):
        if 'num_fetch' in self.request.arguments:
            num_fetch = int(self.get_argument('num_fetch'))
        else:
            num_fetch = 9
        activities = fetch_num_activities(num_fetch)
        self.write(activities)

class FileThumbnailHandler(web.RequestHandler):
    def get(self, thumb_path):
        self.set_header('Content-Type', 'image/png')
        self.write(get_thumbnail(thumb_path))

handlers = [
    (r"/img/(.*)", web.StaticFileHandler, {"path": "frontend/static/img/"}),
    (r"/css/(.*)", web.StaticFileHandler, {"path": "frontend/static/css/"}),
    (r"/js/(.*)", web.StaticFileHandler, {"path": "frontend/static/js/"}),
    (r"/mustache/(.*)", web.StaticFileHandler, {"path": "frontend/static/mustache/"}),
    (r"/upload-submit", UploadSubmitHandler),
    (r"/file/update", FileUpdateHandler),
    (r"/file/thumbnail/(.*)", FileThumbnailHandler),
    (r"/upload", TemplateRenderHandler('upload.html')),
    (r"/recents", TemplateRenderHandler('recents.html')),
    (r"/recents/fetch", RecentItemsHandler),
    (r"/", TemplateRenderHandler('recents.html'))
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


