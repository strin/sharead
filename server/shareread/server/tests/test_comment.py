from shareread.server.comment import *
import shareread.server.db as db
import os

db.set_testing_mode()

def test_add_comment():
    db.flush_db()
    add_comment(1, 1, 1, 'text1')
    add_comment(1, 1, '1', 'text2')
    comments = get_comments(1)
    assert comments == [dict(threadid=1, commentid=1, userid=1, text='text1'),
        dict(threadid=1, commentid=2, userid='1', text='text2')]


def test_get_all_comments():
    db.flush_db()
    add_comment(1, 1, 1, 'text1')
    add_comment(1, 2, 1, 'text2')
    comments = get_all_comments(1)
    assert comments == [dict(threadid=1, commentid=1, userid=1, text='text1'),
        dict(threadid=2, commentid=1, userid=1, text='text2')]

# TODO(dixiao): more tests
def test_delete_comment():
    pass
