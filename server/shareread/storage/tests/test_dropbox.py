from shareread.storage.dropbox import put_file, get_file, get_url
from StringIO import StringIO

def test_sync_file():
    stream = StringIO(buf='test string')
    put_file('tests/test_sync_file.txt', stream)
    download = get_file('tests/test_sync_file.txt')
    result = download.read()
    assert(result == 'test string')


def test_share_url():
    stream = StringIO(buf='test string')
    put_file('tests/test_sync_file.txt', stream)
    url = get_url('tests/test_sync_file.txt')
    assert(url.find('https://www.dropbox.com/s/') == 0)
    assert(url.find('dl=1') != -1)

