import server
from tornado import (web, ioloop)
from tornado.testing import AsyncHTTPTestCase
import shareread.server.db as db
import shareread.server.user as user
import os
import json
import urllib

db.DB_FILE_NAME = 'shareread.test.sqlite'
application = web.Application(server.handlers, **server.settings)


class TestHandlerBase(AsyncHTTPTestCase):
    def setUp(self):
        # clear db first.
        if os.path.exists(db.DB_FILE_NAME):
            os.remove(db.DB_FILE_NAME)
        super(TestHandlerBase, self).setUp()

    def get_app(self):
        return application


class TestHomeViewHandler(TestHandlerBase):
    def test_load(self):
        response = self.fetch('/', method='GET', follow_redirects=False)
        self.assertEqual(response.code, 200)


    def test_auth(self):
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



