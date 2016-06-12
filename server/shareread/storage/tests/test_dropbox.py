from shareread.storage.dropbox import put_file, get_file, TEST_ACCESS_TOKEN
from StringIO import StringIO

def test_sync_file():
    stream = StringIO(buf='test string')
    put_file(TEST_ACCESS_TOKEN, 'tests/test_sync_file.txt', stream)
    download = get_file(TEST_ACCESS_TOKEN, 'tests/test_sync_file.txt')
    result = download.read()
    assert(result == 'test string')

