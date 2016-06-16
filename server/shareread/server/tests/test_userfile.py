'''
tests for module shareread.server.file.
'''
import shareread.server.db as db
from shareread.server.userfile import *
from datetime import datetime


def test_create_file_entry():
    db.flush_db()
    userid = '1'
    filehash = 'test-a2c1d9'
    create_file_entry(userid, filehash, 'test',
                datetime=datetime.now().isoformat(),
                fileext='pdf'
    )
    assert(kv_meta(userid, filehash)['fileext'] == 'pdf')
    assert(kv_meta(userid, filehash)['filename'] == 'test')


def test_get_file_entry():
    db.flush_db()
    userid = '1'
    filehash = 'test-a2c1d9'
    create_file_entry(userid, filehash, 'test',
                datetime=datetime.now().isoformat(),
                fileext='pdf',
                thumb_path='test.png'
    )
    assert(get_file_entry(userid, filehash)['filename'] == 'test')


def test_update_file_entry():
    db.flush_db()
    userid = '1'
    filehash = 'test-a2c1d9'
    create_file_entry(userid, filehash, 'test',
                datetime=datetime.now().isoformat(),
                fileext='pdf',
                thumb_path='test.png'
    )
    update_file_entry(userid, filehash, filename='test2')
    assert(get_file_entry(userid, filehash)['filename'] == 'test2')


def test_recent_entry():
    db.flush_db()
    userid = '1'
    filehash1 = 'test-a2c1d9'
    filehash2 = 'test-s39s2j'
    filehash3 = 'test-afj23f'
    add_recent_entry(userid, filehash1, action_type=RECENTS_ADD)
    add_recent_entry(userid, filehash2, action_type=RECENTS_ADD)
    add_recent_entry(userid, filehash3, action_type=RECENTS_ADD)
    assert(len(kv_recents(userid)) == 3)
    filehashes = get_recent_entries(userid, 2)
    print filehashes
    assert(filehashes == [filehash3, filehash2])

