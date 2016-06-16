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


def test_kv_store_update():
    redis.flush_db()
    kv = KeyValueStore(scope_name='user-1000')
    kv['meta'] = {
        'user-name': 'tianlin.shi',
        'num-files': 100
    }
    assert(kv['meta']['user-name'] == 'tianlin.shi')
    assert(kv['meta']['num-files'] == 100)
    kv.update({
        'meta': None,
        'gender': 'male'
    })
    assert(kv['meta'] is None)
    assert(kv['gender'] == 'male')


def test_kv_store_mget():
    redis.flush_db()
    kv = KeyValueStore(scope_name='user-1000')
    kv['name'] = 'tim'
    kv['gender'] = 'male'
    assert(kv.mget(['name', 'gender']) == {
        'name': 'tim',
        'gender': 'male'
    })
