from tornado import (ioloop, web)
import hashlib
import json
import string
from datetime import datetime
import random
import urllib2
import os

import shareread.storage as store
import shareread.storage.local as local_store
from shareread.utils import Timer
from shareread.server.utils import (parse_webkitform, parse_filename,
                                    create_thumbnail, get_thumbnail_path)
from shareread.server.userfile import (create_file_entry, update_file_entry, get_file_entry,
                                       add_recent_entry, update_inverted_tags, filter_by_inverted_tags,
                                       RECENTS_ADD, RECENTS_UPDATE, fetch_num_activities)
from shareread.server.user import (user_by_cookie, authorize_google, userid_by_cookie,
                                   create_user_from_google, update_user_cookie,
                                   remove_cookie, user_by_id, all_tags, merge_tags)
from shareread.server.file import (create_file)
from shareread.document.metadata import extract_metadata_from_pdf
from shareread.server.paper import (save_paper_entry, get_paper_entry,
                                    save_paper_url, get_filehash_by_url,
                                    rank_by_inverted_words, InverseIndexingProcess)
import shareread.document.pdf2html as pdf2html
from config import SHAREAD_DOMAIN


def wrap_template(template):
    class UploadHandler(web.RequestHandler):
        def get(self):
            if 'user' in self.__dict__: # with authentication.
                user = dict(
                    name=self.user['name'],
                    email=self.user['email'],
                    meta=self.user['meta']
                )
                self.render(template, user=user)
            else:
                self.render(template)
    return UploadHandler



def authorize(cookie_token):
    '''
    given a cookie_token, return userid.
    if the user has not been authorized, then return None.
    '''
    if not cookie_token:
        return None
    return userid_by_cookie(cookie_token)


def make_cookie_token(service, access_token):
    cookie_raw = service + access_token + datetime.now().isoformat()
    cookie = hashlib.sha256(cookie_raw).hexdigest()
    return cookie


def make_sharead_link(filehash):
    '''
    minimalistic implementation of sharing feature.
    generate a link to sharead view of the paper
    '''
    return SHAREAD_DOMAIN + '/v/' + filehash


def wrap_auth(Handler):
    '''
    given a Handler class, wrap it with user authentication.
    '''
    class WrappedHandler(Handler):
        def get(self, *args, **kwargs):
            if 'cookie' in self.request.arguments: # cookie explicit in request.
                cookie_token = self.get_argument('cookie')
            else:
                cookie_token = self.get_secure_cookie('token')
            userid = authorize(cookie_token)
            user = user_by_id(userid)
            if not user:
                print '[user not auth]'
                self.redirect('/') # red
                return
            else:
                print '[authorized] cookie = ', cookie_token
                self.user = user
                self.userid = userid
                return Handler.get(self, *args, **kwargs)


        def post(self, *args, **kwargs):
            if 'cookie' in self.request.arguments: # cookie explicit in request.
                cookie_token = self.get_argument('cookie')
            else:
                cookie_token = self.get_secure_cookie('token')
            userid = authorize(cookie_token)
            user = user_by_id(userid)
            if not user:
                print '[user not auth]'
                self.redirect('/') # red
                return
            else:
                self.user = user
                self.userid = userid
                return Handler.post(self, *args, **kwargs)
    return WrappedHandler


def load_meta_by_filehash(userid, *filehashes):
    meta_by_filehash = {}
    for filehash in filehashes:
        file_entry = get_file_entry(userid, filehash)
        paper_entry = get_paper_entry(filehash)
        final_entry = file_entry
        # merge paper entry with file entry.
        if paper_entry.get('title'):
            final_entry['title'] = paper_entry['title']
        else:
            final_entry['title'] = file_entry['filename']
        if paper_entry.get('authors'):
            final_entry['authors'] = paper_entry['authors']
        else:
            final_entry['authros'] = []
        file_entry['thumb_static_url'] = store.get_url(get_thumbnail_path(filehash))
        meta_by_filehash[filehash] = final_entry
    return meta_by_filehash


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


def upload_file(userid, filename, ext, data):
    # first, store file.
    filehash = create_file(filename, ext, data)
    print '[upload] start ', userid, filehash
    # add file metadata to user's library.
    upload_datetime = str(datetime.now())
    create_file_entry(userid, filehash, filename,
                      fileext=ext,
                      update_datetime=upload_datetime)
    # extract file metadata.
    print '[upload] extracting metadata'
    metadata = extract_metadata_from_pdf(data)
    print '[upload] saving metadata to db', metadata
    save_paper_entry(filehash, metadata)
    # add event to recents log.
    print '[upload] creating file entry'
    add_recent_entry(userid, filehash, action_type=RECENTS_ADD,
                     action_date=None)
    return filehash


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
        filehash = upload_file(self.userid, filename, ext, data)
        save_paper_url(link, filehash)
        print '[pin]', filename, ext, filehash
        self.write({
            'filehash':filehash,
            'link': make_sharead_link(filehash),
            'filename':filename,
            'response':'OK'
        })


class PinStatusHandler(web.RequestHandler):
    def post(self):
        print '[pin status]'
        link = self.get_argument('link')
        filehash = get_filehash_by_url(link)
        if filehash:
            userid = self.userid
            entry = get_file_entry(userid, filehash)
            if entry:
                self.write({
                    'exists': 1,
                    'filehash': filehash,
                    'link': make_sharead_link(filehash),
                    'filename': entry['filename']
                })
            else:
                self.write({
                    'exists': 0
                })
        else:
            self.write({
                'exists': 0
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
        filehash = upload_file(self.userid, filename, ext, data)
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
        metadata = load_meta_by_filehash(self.userid, filehash)[filehash]
        return self.render('view.html',
                filehash=filehash,
                static_url=store.get_url('html/' + filehash),
                meta=metadata)


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
        update_file_entry(self.userid, filehash, **update_dict)
        add_recent_entry(self.userid, filehash, action_type=RECENTS_UPDATE)
        if 'tags' in update_dict: # update inverted-index table for search.
            update_inverted_tags(self.userid, update_dict['tags'], filehash)
            merge_tags(self.userid, update_dict['tags'])

        self.write({
            'response':'OK'
        })


class FileMetaHandler(web.RequestHandler):
    """
    request file metadata.
    """
    def post(self):
        filehashes = json.loads(self.get_argument('filehashes'))
        print '[meta]', filehashes
        meta_by_filehash = load_meta_by_filehash(self.userid, *filehashes)
        global _userid, _filehashes
        _userid = self.userid
        _filehashes = filehashes
        self.write({
            'meta_by_filehash': meta_by_filehash
        })


class MiscInfoHandler(web.RequestHandler):
    def get(self):
        self.write({
            'all_tags': all_tags(self.userid)
        })


class RecentItemsHandler(web.RequestHandler):
    def get(self):
        if 'num_fetch' in self.request.arguments:
            num_fetch = int(self.get_argument('num_fetch'))
        else:
            num_fetch = 9
        activities = fetch_num_activities(self.userid, num_fetch)
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
        print 'tags', tags
        print 'keywords', keywords
        filehashes = None
        if not tags:
            tags = []
        filehashes = filter_by_inverted_tags(self.userid, tags)
        filehashes = list(filehashes) # json convertible.
        filehashes = rank_by_inverted_words(keywords, filehashes)
        print '[search] result as filehashes', filehashes
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
    (r"/upload-submit", wrap_auth(UploadSubmitHandler)),
    (r"/pin-submit", wrap_auth(PinSubmitHandler)),
    (r"/pin-status", wrap_auth(PinStatusHandler)),
    (r"/v/(.*)", wrap_auth(FileViewHandler)),
    (r"/file/update", wrap_auth(FileUpdateHandler)),
    (r"/file/meta", wrap_auth(FileMetaHandler)),
    (r"/file/thumbnail/(.*)", FileThumbnailHandler),
    (r"/file/download/(.*)", FileDownloadHanlder),
    (r"/db/misc", wrap_auth(MiscInfoHandler)),
    (r"/search", wrap_auth(SearchHandler)),
    (r"/upload", wrap_template('upload.html')),
    (r"/recents", wrap_auth(wrap_template('recents.html'))),
    (r"/recents/fetch", wrap_auth(RecentItemsHandler)),
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
    # start inverse indexing.
    inverse_indexing_process = InverseIndexingProcess()
    inverse_indexing_process.start()

    # start main application.
    application = web.Application(handlers, **settings)
    port = int(os.environ.get("PORT", 5000))
    application.listen(port, address="0.0.0.0")
    ioloop.IOLoop.current().start()


