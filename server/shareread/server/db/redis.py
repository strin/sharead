'''
this is a key-value store wrapper around redis.
'''
import redis
from os import environ
import json
from datetime import datetime

_redis_store = None

def conn():
    global _redis_store
    if not _redis_store: # establish a new connection.
        if 'REDIS_URL' in environ:
            _redis_store = redis.StrictRedis.from_url(environ.get('REDIS_URL'))
        else:
            _redis_store = redis.StrictRedis(host='localhost', port=6379, db=0)
    return _redis_store


def set_testing_mode():
    global _redis_store
    import fakeredis
    _redis_store = fakeredis.FakeStrictRedis()


def flush_db():
    _redis_store.flushdb()


def loads(raw, default=None):
    if raw:
        return json.loads(raw)
    return default


def dumps(obj):
    return json.dumps(obj)


class KeyValueStore(object):
    '''
    a simple model template for key-value stores.
    '''
    def __init__(self, scope_name=None):
        '''
        scope_name: scope of the key-value store.
        if scope_name is None, then it uses the entire redis db as key-value store.
        '''
        self.conn = conn()
        self.scope_name = scope_name


    def __getitem__(self, key):
        '''
        usage: store[key]
        return the value corresponding to the key in DB.
        '''
        if self.scope_name:
            raw = self.conn.hget(self.scope_name, key)
        else:
            raw = self.conn.get(key)
        return loads(raw)


    def __contains__(self, key):
        return key in self.conn


    def __setitem__(self, key, value):
        if self.scope_name:
            return self.conn.hset(self.scope_name, key, dumps(value))
        else:
            return self.conn.set(key, dumps(value))


    def remove(self, key):
        return self.conn.delete(key)




