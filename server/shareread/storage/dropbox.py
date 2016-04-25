import external.dropbox as dbx

APP_KEY   = '1gtl0f8cj9tj6j9'
APP_SECRET = 'dshgb079kgt8qmr'
TEST_ACCESS_TOKEN = 'F32ygv2k14cAAAAAAAFY9rqPb-xtlAh9wzRJZSLfQ-brGFCDAa5rKZdzpywb6Td1' #TODO: remove.

def _get_access_token():
    """
    Returns a url using which users can log in Dropbox and get access token
    for us.
    """
    flow = dbx.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_SECRET)
    authorize_url = flow.start()
    return authorize_url

def put_file(access_token, path, stream):
    """
    Use the access_token to put the file in Dropbox path.
    """
    print '<<<<< put file >>>>>>'
    client = dbx.client.DropboxClient(access_token)
    response = client.put_file(path, stream)
    return response #(TODO) wrap the response.

def get_file(access_token, path):
    """
    Use the access_token to get file from path.
    Return a stream.
    """
    client = dbx.client.DropboxClient(access_token)
    stream, metadata = client.get_file_and_metadata(path)
    return stream

def account_info(access_token):
    client = dbx.client.DropboxClient(access_token)
    return client.account_info()


if __name__ == '__main__':
    print 'authorize_url', _get_access_token()
