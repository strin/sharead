import external.dropbox as dbx

APP_KEY   = '1gtl0f8cj9tj6j9'
APP_TOKEN = '5osbesiib74rgyh'

def _get_access_token():
    """
    Returns a url using which users can log in Dropbox and get access token
    for us.
    """
    flow = dbx.client.DropboxOAuth2FlowNoRedirect(APP_KEY, APP_TOKEN)
    authorize_url = flow.start()
    return authorize_url

def put_file(access_token, path, stream):
    """
    Use the access_token to put the file in Dropbox path.
    """
    with dbx.client.DropboxClient(access_token) as client:
        response = client.put_file(paht, stream)
        return response #(TODO) wrap the response.

def get_file(access_token, path):
    """
    Use the access_token to get file from path.
    Return a stream.
    """
    with dbx.client.DropboxClient(access_token) as client:
        stream, metadata = client.get_file_and_metadata(path)
        return stream
