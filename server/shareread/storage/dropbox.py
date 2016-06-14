### dropbox client has the following shortfalls: CORS (dropbox.com), slow (dropbox api).
import external.dropbox as dbx
from .local import get_file as local_get_file

# TODO: insecure. test purpose only.
APP_KEY   = '1gtl0f8cj9tj6j9'
APP_SECRET = 'dshgb079kgt8qmr'
ACCESS_TOKEN = 'F32ygv2k14cAAAAAAAFY9rqPb-xtlAh9wzRJZSLfQ-brGFCDAa5rKZdzpywb6Td1'

def _get_access_token():
    """
    Returns a url using which users can log in Dropbox and get access token
    for us.
    """
    flow = dbx.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    authorize_url = flow.start()
    return authorize_url

def put_file(path, stream):
    """
    Use the access_token to put the file in Dropbox path.
    """
    client = dbx.client.DropboxClient(ACCESS_TOKEN)
    response = client.put_file(path, stream, overwrite=True)
    return response #(TODO) wrap the response.

def get_file(path):
    """
    Use the access_token to get file from path.
    Return a stream.
    """
    client = dbx.client.DropboxClient(ACCESS_TOKEN)
    stream, metadata = client.get_file_and_metadata(path)
    print 'metadata', metadata
    return stream

def account_info():
    client = dbx.client.DropboxClient(ACCESS_TOKEN)
    return client.account_info()


def get_url(path):
    client = dbx.client.DropboxClient(ACCESS_TOKEN)
    link = client.share(path, short_url=False)[u'url']
    link = link.replace('dl=0', 'dl=1') # set dl=1, direct download.
    return link


def put_file_from_local(path, local_path):
    stream = local_get_file(local_path)
    put_file(path, stream)
    stream.close()


if __name__ == '__main__':
    print 'authorize_url', _get_access_token()
