import shareread.server.db.redis as redis
from shareread.server.db.redis import KeyValueStore

redis.set_testing_mode()

def test_kv_store():
    redis.flush_db()
    kv = KeyValueStore(scope_name=None)
    kv['meta'] = {
        'site-name': 'sharead',
        'num-users': 1000
    }
    assert(kv['meta']['site-name'] == 'sharead')
    assert(kv['meta']['num-users'] == 1000)


def test_scoped_kv_store():
    redis.flush_db()
    kv = KeyValueStore(scope_name='user-1000')
    kv['meta'] = {
        'user-name': 'tim.shi',
        'num-files': 100
    }
    kv = KeyValueStore(scope_name='user-101')
    assert('meta' not in kv)
    kv = KeyValueStore(scope_name='user-1000')
    assert(kv['meta']['user-name'] == 'tim.shi')
    assert(kv['meta']['num-files'] == 100)
