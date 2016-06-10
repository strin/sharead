from shareread.server.user import create_user_from_google, authorize_google, userid_by_googleid
import shareread.server.db as db
import os


def cleanup_db():
    if os.path.exists(db.DB_FILE_NAME):
        os.remove(db.DB_FILE_NAME)


def test_create_user():
    cleanup_db()
    userid = create_user_from_google(googleid='1', name='Tim',
            email='tim@sharead.org',
            access_token='xxxxx'
        )
    assert userid_by_googleid('1') == userid
    assert authorize_google('xxxxx') == userid

