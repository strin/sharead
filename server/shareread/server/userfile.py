'''
this module provides high-level functions to upload, access and retrive files.
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


def create_file_entry(userid, filehash, filename, **kwargs):
    data = dict(filehash=filehash, filename=filename)
    data.update(kwargs)
    kv_meta(userid, filehash).update(data)


def get_file_entry(userid, filehash):
    entry = kv_meta(userid, filehash).mget([
        'filename', 'thumb_path'
    ])
    entry[filehash] = filehash
    return entry


def update_file_entry(userid, filehash, **kwargs):
    # allowed modifications keys.
    whitelist = set([
        "filename",
        "fileext",
        "tags",
        "upload_date"
        "thumb_path"
    ])
    kv_meta(userid, filehash).update(
        {k: v for (k, v) in kwargs.items() if k in whitelist}
    )


RECENTS_ADD = 'RECENTS_ADD'
RECENTS_DELETE = 'RECENTS_DELETE'
RECENTS_UPDATE = 'RECENTS_UPDATE'

def get_recent_entries(userid, num_entries):
    entries = kv_recents(userid)[-1:0]
    print 'entries', entries
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

def fetch_num_activities(num_fetch):
    # first pass: fetch filehashes in order.
    filehashes = get_recent_entries(num_fetch)
    return {
        'filehashes':filehashes,
    }


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


def create_file(filename, ext, data):
    data_stream = StringIO(data)
    # get filehash.
    md5_code = hashlib.md5(data).digest()
    filehash = base64.urlsafe_b64encode(md5_code)
    # first, process files locally on server.
    # the server might have ephermal memory, so the files created are temporary.
    pdf_path = 'pdf/' + filehash
    local_store.put_file('upload/' + pdf_path, data_stream)
    # 1. render html
    html_path = 'html/' + filehash
    pdf2html.render_html_from_pdf(
        local_store.get_local_path('upload/' + pdf_path),
        local_store.get_local_path('upload/' + html_path)
    )
    # 2. render thumbnail.
    thumb_path = get_thumbnail_path(filehash)
    create_thumbnail(
        local_store.get_local_path('upload/' + pdf_path),
        local_store.get_local_path('upload/' + thumb_path)
    )

    # upload results to permanent storage.
    store.put_file_from_local('html/' + filehash, 'upload/' + html_path)
    store.put_file_from_local(get_thumbnail_path(filehash), 'upload/' + thumb_path)
    data_stream.seek(0)
    store.put_file('paper/' + filehash, data_stream)
    data_stream.close()

    with Timer('share urls'):
        print 'paper url', store.get_url('paper/' + filehash)
        print 'html url', store.get_url('html/' + filehash)
        print 'thumb url', store.get_url(get_thumbnail_path(filehash))
    # create html view.
    # get upload date.
    upload_date = str(datetime.now())

    # update db.
    create_file_entry(filehash, filename, ext, upload_date, thumb_path=thumb_path)
    add_recent_entry(filehash, action_type=RECENTS_ADD)
    return filehash

