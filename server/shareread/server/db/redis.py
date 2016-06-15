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
    def __init__(self, db_name):
        '''
        db_name: name of the key-value store database.
        '''
        self.conn = conn()
        self.db_name = 'kv:' + db_name
        self.wrap_key = lambda key: self.db_name + ':' + key


    def __getitem__(self, key):
        '''
        usage: store[key]
        return the value corresponding to the key in DB.
        '''
        raw = self.conn.get(self.wrap_key(key))
        return loads(raw)


    def __contains__(self, key):
        return self.wrap_key(key) in self.conn


    def __setitem__(self, key, value):
        return self.conn.set(self.wrap_key(key), dumps(value))


    def remove(self, key):
        return self.conn.delete(self.wrap_key(key))




def get_recent_entries(num_entries):
    """
    use DBConn to get num_entries of recent entries
    return filehashes reversely oredered in time
    """
    entries = conn().zrange('recents', 0, -1, desc=True)
    filehashes = []
    filehash_set = set()
    for entry in entries:
        entry = loads(entry)
        filehash = entry['filehash']
        if filehash not in filehash_set:
            filehashes.append(filehash)
            filehash_set.add(filehash)
        if len(filehashes) > num_entries:
            break
    return filehashes


def add_recent_entry(filehash, action_type, action_date = None):
    """
    use DBConn to add a file entry action to recents
    Parameter
    ======
        filehash
        action_type: recents.RECENTS_ADD, recents.RECENTS_DELETE, recents.RECENTS_UPDATE
        action_date: date of last operation, default - current time.
    """
    if not action_date:
        action_date = str(datetime.now())
    rowid = conn().zcount('recents', -float('inf'), float('inf'))
    conn().zadd('recents', rowid, dumps(dict(
            filehash=filehash,
            action_date=action_date,
            action_type=action_type
        ))
    )


def get_file_entry(filehash):
    """
    use DBConn to get a file entry by filehash.
    Parameter
    ======
        filehash
    """
    row = conn().hget('meta', filehash)
    return loads(row)


def update_file_entry(filehash, **kwargs):
    """
    use DBConn to update a file entry incrementally.
    Parameter
    =========
    filehash: required, to identify the file entry
    kwargs: a dict of key-value modifications.
    """
    # allowed modifications keys.
    whitelist = set([
        "filename",
        "fileext",
        "tags",
        "upload_date"
        "thumb_path"
    ])
    # merge into global tags.
    if 'tags' in kwargs:
        MiscInfo().merge_tags(kwargs['tags'])

    old_entry = get_file_entry(filehash)

    new_entry = dict(old_entry)
    kwargs = {key: value
              for (key, value) in kwargs.items() if key in whitelist}
    new_entry.update(kwargs)
    print 'new_entry', new_entry

    conn().hset('meta', filehash, dumps(new_entry))


def update_inverted_index(tags, filehash):
    """
    use DBConn to update the inverted index table
    """
    for tag in tags:
        filehashes = conn().hget('inverted', tag)
        filehashes = loads(filehashes, default=[])
        filehashes.append(filehash)
        conn().hset('inverted', tag, dumps(filehashes))


def filter_by_inverted_index(tags):
    """
    use DBConn to filter the filehashes based on the tags given
    """
    result = None
    for tag in tags:
        filehashes = loads(conn().hget('inverted', tag))
        if filehashes:
            filehash_set = set(filehashes)
            result = result.intersection(filehash_set) if result else filehash_set
    return result if result else set()

