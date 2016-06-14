from shareread.storage.s3 import put_file, get_file, get_url
from StringIO import StringIO
import urllib2

def test_sync_file():
    stream = StringIO(buf='test string')
    put_file('tests/test_sync_file.txt', stream)
    download = get_file('tests/test_sync_file.txt')
    result = download.read()
    print 'result', result
    assert(result == 'test string')


def test_share_url():
    stream = StringIO(buf='test string')
    put_file('tests/test_sync_file.txt', stream)
    url = get_url('tests/test_sync_file.txt')
    print 'url', url
    result = urllib2.urlopen(url).read()
    print 'reuslt', result
    assert(result == 'test string')

