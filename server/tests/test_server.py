import server
from tornado import (web, ioloop)
from tornado.testing import AsyncHTTPTestCase
import shareread.server.db as db
import os

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
