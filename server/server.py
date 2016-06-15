from tornado import (ioloop, web)
import md5
import hashlib
import base64
import json
import string
from StringIO import StringIO
from datetime import datetime
import random
import urllib2
import os

#import shareread.storage.dropbox as store
import shareread.storage as store
import shareread.storage.local as local_store
from shareread.utils import Timer
from shareread.server.utils import (parse_webkitform, parse_filename,
                                    create_thumbnail, get_thumbnail_path)
from shareread.server.db import (create_file_entry, update_file_entry, get_file_entry,
                                 add_recent_entry, update_inverted_index, filter_by_inverted_index,
                                 MiscInfo)
from shareread.server.recents import (RECENTS_ADD, RECENTS_UPDATE, fetch_num_activities)
from shareread.server.user import (user_by_cookie, authorize_google, create_user_from_google, update_user_cookie, remove_cookie)
import shareread.document.pdf2html as pdf2html


def wrap_template(template):
    class UploadHandler(web.RequestHandler):
        def get(self):
            if 'user' in self.__dict__: # with authentication.
                user = dict(
                    name=self.user.get('name'),
                    email=self.user.get('email'),
                    meta=self.user.get('meta')
                )
                self.render(template, user=user)
            else:
                self.render(template)
    return UploadHandler


def create_file(filename, ext, data):
    data_stream = StringIO(data)
    # get filehash.
    md5_code = md5.new()
    md5_code.update(data)
    filehash = base64.urlsafe_b64encode(md5_code.digest())
    # first, process files locally on server.
    # the server might have ephermal memory, so the files created are temporary.
    pdf_path = 'pdf/' + filehash
    local_store.put_file('upload/' + pdf_path, data_stream)
    # 1. render html
    html_path = 'html/' + filehash
    pdf2html.render_html_from_pdf(
        local_store.get_local_path('upload/' + pdf_path),
        local_store.get_local_path('upload/' + html_path)
    )
    # 2. render thumbnail.
    thumb_path = get_thumbnail_path(filehash)
    create_thumbnail(
        local_store.get_local_path('upload/' + pdf_path),
        local_store.get_local_path('upload/' + thumb_path)
    )

    # upload results to permanent storage.
    store.put_file_from_local('html/' + filehash, 'upload/' + html_path)
    store.put_file_from_local(get_thumbnail_path(filehash), 'upload/' + thumb_path)
    data_stream.seek(0)
    store.put_file('paper/' + filehash, data_stream)
    data_stream.close()

    with Timer('share urls'):
        print 'paper url', store.get_url('paper/' + filehash)
        print 'html url', store.get_url('html/' + filehash)
        print 'thumb url', store.get_url(get_thumbnail_path(filehash))
    # create html view.
    # get upload date.
    upload_date = str(datetime.now())

    # update db.
    create_file_entry(filehash, filename, ext, upload_date, thumb_path=thumb_path)
    add_recent_entry(filehash, action_type=RECENTS_ADD)
    return filehash


def authorize(cookie_token):
    '''
    given a cookie_token, return userid.
    if the user has not been authorized, then return None.
    '''
    if not cookie_token:
        return None
    return user_by_cookie(cookie_token)


def make_cookie_token(service, access_token):
    cookie_raw = service + access_token + datetime.now().isoformat()
    cookie = hashlib.sha256(cookie_raw).hexdigest()
    return cookie


def wrap_auth(Handler):
    '''
    given a Handler class, wrap it with user authentication.
    '''
    class WrappedHandler(Handler):
        def get(self, *args, **kwargs):
            cookie_token = self.get_secure_cookie('token')
            user = authorize(cookie_token)
            if not user:
                self.redirect('/') # red
                return
            else:
                print '[authorized] cookie = ', cookie_token
                self.user = user
                return Handler.get(self, *args, **kwargs)


        def post(self, *args, **kwargs):
            cookie_token = self.get_secure_cookie('token')
            user = authorize(cookie_token)
            if not user:
                self.redirect('/') # red
                return
            else:
                self.user = user
                return Handler.post(self, *args, **kwargs)
    return WrappedHandler


class AuthenticateHandler(web.RequestHandler):
    ''' AJAX authentication handler'''
    def post(self):
        service = self.get_argument('service')
        access_token = self.get_argument('access_token')
        name = self.get_argument('name')
        email = self.get_argument('email')
        cookie_token = make_cookie_token(service, access_token)
        if service == 'google':
            # first try login.
            googleid = self.get_argument('googleid')
            image_url = self.get_argument('image_url',
                    default='/img/default-profile.jpg')
            userid = authorize_google(access_token)
            if not userid: # create an account if necessary.
                userid = create_user_from_google(googleid=googleid,
                        name=name,
                        email=email,
                        access_token=access_token,
                        meta={
                            'image_url': image_url
                        }
                    )
            update_user_cookie(cookie_token, userid)
            print '[setting cookie]', cookie_token
            self.set_secure_cookie('token', cookie_token)
            self.write({
                'response': 'OK',
                'cookie_token': cookie_token
            })
        else:
            self.write({
                'response': 'ERROR',
                'message': 'unknown service'
            })


class LogoutHandler(web.RequestHandler):
    ''' AJAX logout handler'''
    def post(self):
        cookie_token = self.get_secure_cookie('token')
        print 'delete cookie', cookie_token
        if cookie_token:
            remove_cookie(cookie_token)
        self.write({
            'response': 'OK'
        })

    def get(self):
        return self.post()



class PinSubmitHandler(web.RequestHandler):
    def post(self):
        link = self.get_argument('link')
        filename_full = link[link.rfind('/')+1:]
        (filename, ext) = parse_filename(filename_full)
        stream = urllib2.urlopen(link)
        data = stream.read()
        filehash = create_file(filename, ext, data)
        print '[pin]', filename, ext, filehash
        self.write({
            'filehash':filehash,
            'filename':filename,
            'response':'OK'
        })



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
        filehash = create_file(filename, ext, data)
        print '[upload]', filename, ext, filehash
        self.write({
            'filehash':filehash,
            'filename':filename,
            'response':'OK'
        })


class FileDownloadHanlder(web.RequestHandler):
    def get(self, filehash):
        data = store.get_file('paper/' + filehash).read()
        self.set_header('Content-Type', 'application/pdf')
        self.write(data)


class FileViewHandler(web.RequestHandler):
    def get(self, filehash):
        file_entry = get_file_entry(filehash)
        return self.render('view.html',
                filehash=filehash,
                static_url=store.get_url('html/' + filehash),
                meta=file_entry)


class FileUpdateHandler(web.RequestHandler):
    def post(self):
        arguments = set(self.request.arguments)
        # filehash is required.
        filehash = json.loads(self.get_argument('filehash'))
        update_dict = dict()
        ##TODO(tianlins): isolate encoder/decoding for updates.
        for key in arguments:
            if key == 'filehash':
                continue
            value = json.loads(self.get_argument(key))
            update_dict[key] = value
        # update db.
        update_file_entry(filehash, **update_dict)
        add_recent_entry(filehash, action_type=RECENTS_UPDATE)
        if 'tags' in update_dict: # update inverted-index table for search.
            update_inverted_index(update_dict['tags'], filehash)
        self.write({
            'response':'OK'
        })

class FileMetaHandler(web.RequestHandler):
    """
    request file metadata.
    """
    def post(self):
        filehashes = json.loads(self.get_argument('filehashes'))
        meta_by_filehash = {filehash: get_file_entry(filehash) for filehash in filehashes}
        for filehash, entry in meta_by_filehash.items():
            if 'thumb_path' in entry:
                entry['thumb_static_url'] = store.get_url(get_thumbnail_path(filehash))
                print entry
        self.write({
            'meta_by_filehash': meta_by_filehash
        })

class MiscInfoHandler(web.RequestHandler):
    def get(self):
        misc = MiscInfo()
        self.write({
            'all_tags': misc.all_tags
        })

class RecentItemsHandler(web.RequestHandler):
    def get(self):
        if 'num_fetch' in self.request.arguments:
            num_fetch = int(self.get_argument('num_fetch'))
        else:
            num_fetch = 9
        activities = fetch_num_activities(num_fetch)
        for filehash, entry in activities.items():
            if 'thumb_path' in entry:
                entry['thumb_static_url'] = store.get_url(get_thumbnail_path(filehash))
                print entry
        self.write(activities)

class FileThumbnailHandler(web.RequestHandler):
    def get(self, filehash):
        self.set_header('Content-Type', 'image/png')
        stream = store.get_file(get_thumbnail_path(filehash))
        self.write(stream.read())
        stream.close()


class SearchHandler(web.RequestHandler):
    """
    Handles search / filter requests from client
    Each request is a HTTP Post with the following arguments:
        tags (list of JSON-encoded str): a list of file tags.
        keywords (JSON-encoded str): a string of search input.
    """
    def post(self):
        tags = json.loads(self.get_argument('tags'))
        keywords = json.loads(self.get_argument('keywords'))
        filehashes = filter_by_inverted_index(tags)
        filehashes = list(filehashes) # json convertible.
        self.write({
            'filehashes': filehashes
        })

handlers = [
    (r"/img/(.*)", web.StaticFileHandler, {"path": "frontend/static/img/"}),
    (r"/css/(.*)", web.StaticFileHandler, {"path": "frontend/static/css/"}),
    (r"/js/(.*)", web.StaticFileHandler, {"path": "frontend/static/js/"}),
    (r"/coffee/(.*)", web.StaticFileHandler, {"path": "frontend/static/coffee/"}),
    (r"/fonts/(.*)", web.StaticFileHandler, {"path": "frontend/static/fonts/"}),
    (r"/mustache/(.*)", web.StaticFileHandler, {"path": "frontend/static/mustache/"}),
    (r"/upload-submit", UploadSubmitHandler),
    (r"/pin-submit", PinSubmitHandler),
    (r"/v/(.*)", FileViewHandler),
    (r"/file/update", FileUpdateHandler),
    (r"/file/meta", FileMetaHandler),
    (r"/file/thumbnail/(.*)", FileThumbnailHandler),
    (r"/file/download/(.*)", FileDownloadHanlder),
    (r"/db/misc", MiscInfoHandler),
    (r"/search", SearchHandler),
    (r"/upload", wrap_template('upload.html')),
    (r"/recents", wrap_auth(wrap_template('recents.html'))),
    (r"/recents/fetch", RecentItemsHandler),
    (r"/home", wrap_auth(wrap_template('recents.html'))),
    (r"/auth", AuthenticateHandler),
    (r"/logout", LogoutHandler),
    (r"/", wrap_template('index.html'))
]

settings = {
    "autoreload": True,
    "debug": True,
    "template_path": "frontend/template/",
    "cookie_secret": hashlib.sha256(''.join([
        random.choice(string.ascii_uppercase) for i in range(100)
    ])).hexdigest()
}

if __name__ == "__main__":
    application = web.Application(handlers, **settings)
    port = int(os.environ.get("PORT", 5000))
    application.listen(port, address="0.0.0.0")
    ioloop.IOLoop.current().start()


