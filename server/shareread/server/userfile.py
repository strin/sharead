'''
this module provides functions to manipuate user's file metadata.
'''
from shareread.utils import Timer
import shareread.storage as store
import shareread.storage.local as local_store
import shareread.document.pdf2html as pdf2html
from shareread.server.utils import (create_thumbnail, get_thumbnail_path)
from shareread.server.db import KeyValueStore, SortedList
#from shareread.server.recents import (RECENTS_ADD)

from StringIO import StringIO
import hashlib
import base64
from datetime import datetime

# user-dependent file meta data.
kv_meta = lambda userid, filehash: KeyValueStore('meta:' + userid + ':' + filehash)

# recent actions to files by user.
kv_recents = lambda userid: SortedList('recents:' + userid)

# inverted search by tags.
kv_inverted = lambda userid: KeyValueStore('inverted:' + userid)


def create_file_entry(userid, filehash, filename, **kwargs):
    data = dict(filehash=filehash, filename=filename)
    data.update(kwargs)
    kv_meta(userid, filehash).update(data)


def get_file_entry(userid, filehash):
    entry = kv_meta(userid, filehash).mget([
        'filename', 'tags'
    ])
    if not entry:
        return None
    entry['filehash'] = filehash
    if not entry.get('tags'):
        entry['tags'] = []
    return entry


def update_file_entry(userid, filehash, **kwargs):
    # allowed modifications keys.
    whitelist = set([
        "filename",
        "fileext",
        "tags",
        "upload_datetime"
    ])
    kv_meta(userid, filehash).update(
        {k: v for (k, v) in kwargs.items() if k in whitelist}
    )


RECENTS_ADD = 'RECENTS_ADD'
RECENTS_DELETE = 'RECENTS_DELETE'
RECENTS_UPDATE = 'RECENTS_UPDATE'

def get_recent_entries(userid, num_entries):
    entries = kv_recents(userid)[-1:0]
    filehashes = []
    filehash_set = set()
    for entry in entries:
        entry = entry
        filehash = entry['filehash']
        if filehash not in filehash_set:
            filehashes.append(filehash)
            filehash_set.add(filehash)
        if len(filehashes) >= num_entries:
            break
    return filehashes


def add_recent_entry(userid, filehash, action_type, action_date = None):
    """
    Parameter
    ======
        filehash
        action_type: recents.RECENTS_ADD, recents.RECENTS_DELETE, recents.RECENTS_UPDATE
        action_date: date of last operation, default - current time.
    """
    if not action_date:
        action_date = str(datetime.now())
    _kv_recents = kv_recents(userid)
    rowid = len(_kv_recents)
    _kv_recents.append(dict(
        filehash=filehash,
        action_date=action_date,
        action_type=action_type
    ), rowid)

def fetch_num_activities(userid, num_fetch):
    # first pass: fetch filehashes in order.
    filehashes = get_recent_entries(userid, num_fetch)
    return {
        'filehashes':filehashes,
    }


def update_inverted_index(userid, tags, filehash):
    """
    update the inverted index table
    """
    for tag in tags:
        filehashes = kv_inverted(userid)[tag]
        if not filehashes:
            filehashes = []
        filehashes.append(filehash)
        kv_inverted(userid)[tag] = filehashes


def filter_by_inverted_index(userid, tags):
    """
    filter the filehashes based on the tags given
    """
    result = None
    for tag in tags:
        filehashes = kv_inverted(userid)[tag]
        if filehashes:
            filehash_set = set(filehashes)
            result = result.intersection(filehash_set) if result else filehash_set
    return result if result else set()


