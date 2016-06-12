from tornado import (ioloop, web)
import md5
import hashlib
import base64
import json
from StringIO import StringIO
from datetime import datetime
import urllib2
import os

#import shareread.storage.dropbox as store
import shareread.storage as store
from shareread.server.utils import (parse_webkitform, parse_filename,
                                    create_thumbnail, get_thumbnail)
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
    filehash = '.'.join([filehash, ext])
    # save file to store.
    store.put_file(store.TEST_ACCESS_TOKEN, 'paper/' + filehash, data_stream)
    # create html view.
    pdf2html.render_html_from_pdf(filehash, data_stream)
    # get upload date.
    upload_date = str(datetime.now())
    # create thumbnail.
    thumb_path = create_thumbnail(filehash)
    # update db.
    create_file_entry(filehash, filename, ext, upload_date, thumb_path=thumb_path)
    add_recent_entry(filehash, action_type=RECENTS_ADD)
    return filehash


def authorize(cookie_token):
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
            cookie_token = self.get_cookie('token')
            user = authorize(cookie_token)
            if not user:
                self.redirect('/') # red
                return
            else:
                print '[authorized] cookie = ', cookie_token
                self.user = user
                return Handler.get(self, *args, **kwargs)


        def post(self, *args, **kwargs):
            cookie_token = self.get_cookie('token')
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
            self.set_cookie('token', cookie_token)
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
        cookie_token = self.get_cookie('token')
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
        data = store.get_file(store.TEST_ACCESS_TOKEN, 'paper/' + filehash).read()
        self.set_header('Content-Type', 'application/pdf')
        self.write(data)


class FileHTMLHandler(web.RequestHandler):
    def get(self, filehash):
        html_path = pdf2html.get_rendered_path(filehash)
        with open(html_path, 'r') as f:
            self.set_header('Content-Type', 'text/html')
            self.write(f.read())


class FileViewHandler(web.RequestHandler):
    def get(self, filehash):
        file_entry = get_file_entry(filehash)
        return self.render('view.html', 
                filehash=filehash,
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
        self.write({
            'meta_by_filehash':meta_by_filehash
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
        self.write(activities)

class FileThumbnailHandler(web.RequestHandler):
    def get(self, thumb_path):
        self.set_header('Content-Type', 'image/png')
        self.write(get_thumbnail(thumb_path))

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
    (r"/file/html/(.*)", FileHTMLHandler),
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
    "template_path": "frontend/template/"
}

if __name__ == "__main__":
    application = web.Application(handlers, **settings)
    port = int(os.environ.get("PORT", 5000))
    application.listen(port, address="0.0.0.0")
    ioloop.IOLoop.current().start()


