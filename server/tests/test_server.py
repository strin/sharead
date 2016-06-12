import server
from tornado import (web, ioloop)
from tornado.testing import AsyncHTTPTestCase
import shareread.server.db as db
import shareread.server.user as user
import os
import json
import urllib
import mock

application = web.Application(server.handlers, **server.settings)

db.set_testing_mode()

# tornado test client does not support cookie.
# we need to create a mock.
cookie = {}
def set_cookie(obj, k, v):
    cookie[k] = v

def get_cookie(obj, k):
    return cookie[k]

web.RequestHandler.set_cookie = set_cookie
web.RequestHandler.set_secure_cookie = set_cookie
web.RequestHandler.get_cookie = get_cookie
web.RequestHandler.get_secure_cookie = get_cookie


class TestHandlerBase(AsyncHTTPTestCase):
    def setUp(self):
        # clear db first.
        super(TestHandlerBase, self).setUp()

    def get_app(self):
        return application


class TestHomeViewHandler(TestHandlerBase):
    def test_load(self):
        db.flush_db()
        response = self.fetch('/', method='GET', follow_redirects=False)
        self.assertEqual(response.code, 200)


    def test_auth(self):
        db.flush_db()
        args = dict(
            access_token='xxxxx',
            googleid='1',
            service='google',
            name='Tim',
            email='tim@sharead.org'
        )
        encoded = urllib.urlencode(args)
        response = self.fetch('/auth?' + encoded, method='POST',
                body=json.dumps({}),
                follow_redirects=False)
        message = json.loads(response.buffer.read())
        self.assertEqual(response.code, 200)
        self.assertEqual(message['response'], 'OK')
        cookie_token = message['cookie_token']
        u = user.user_by_cookie(cookie_token)
        for key in ['name', 'email']:
            self.assertEqual(u[key], args[key])


    def test_home(self):
        '''
        test recents page with authentication wrapper.
        '''
        db.flush_db()
        # without authentication.
        response = self.fetch('/home', follow_redirects=False)
        self.assertEqual(response.code, 302) # redirect.
        # authorize and try again.

        args = dict(
            access_token='xxxxx',
            googleid='1',
            service='google',
            name='Tim',
            email='tim@sharead.org'
        )
        encoded = urllib.urlencode(args)
        self.fetch('/auth?' + encoded, method='POST',
                body=json.dumps({}),
                follow_redirects=False)

        response = self.fetch('/home', method='GET', follow_redirects=False)
        self.assertEqual(response.code, 200) # redirect.
        # logout and try again.
        response = self.fetch('/logout', method='GET')
        print response
        response = self.fetch('/home', method='GET', follow_redirects=False)
        self.assertEqual(response.code, 302) # redirect.



