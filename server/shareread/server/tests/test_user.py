from shareread.server.user import *
import shareread.server.db as db
import os

db.set_testing_mode()

def test_create_user():
    db.flush_db()
    userid = create_user_from_google(googleid='1', name='Tim',
            email='tim@sharead.org',
            access_token='xxxxx'
        )
    assert userid_by_googleid('1') == userid
    assert authorize_google('xxxxx') == userid


def test_merge_tags():
    db.flush_db()
    userid = create_user_from_google(googleid='1', name='Tim',
            email='tim@sharead.org',
            access_token='xxxxx'
        )
    tags = all_tags(userid)
    assert(type(tags) == list and tags == [])
    merge_tags(userid, ['icml'])
    assert(all_tags(userid) == ['icml'])


