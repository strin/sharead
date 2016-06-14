from boto.s3.connection import S3Connection
from boto.s3.key import Key
from .local import get_file as local_get_file
from StringIO import StringIO

S3_BUCKET = 'sharead'

# TODO: insecure. test purpose only.
APP_KEY = 'AKIAICZ3PNUZOWOWGK4Q'
APP_SECRET = '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'

class S3Conn(object):
    def __enter__(self):
        self.s3conn = S3Connection(APP_KEY, APP_SECRET)
        self.bucket = self.s3conn.get_bucket(S3_BUCKET)
        return self


    def __exit__(self, type, value, traceback):
        self.s3conn.close()


def put_file(path, stream):
    with S3Conn() as conn:
        item = Key(conn.bucket)
        item.key = path
        item.set_contents_from_string(stream.read())


def get_url(path, expire=3600):
    try:
        with S3Conn() as conn:
            item = Key(conn.bucket)
            item.key = path
            return item.generate_url(expire)
    except S3ResponseError as error:
        return ''


def get_file(path):
    with S3Conn() as conn:
        item = Key(conn.bucket)
        item.key = path
        stream = StringIO(item.get_contents_as_string())
        return stream


def put_file_from_local(path, local_path):
    stream = local_get_file(local_path)
    put_file(path, stream)
    stream.close()
