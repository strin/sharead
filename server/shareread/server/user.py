from shareread.server.db import KeyValueStore
import hashlib
import base64

kv_auth_google = lambda: KeyValueStore('auth_google') # token -> {'userid': 1, 'expired': false}
kv_user_google = lambda: KeyValueStore('user_google') # google_user_id -> user_id
kv_cookie = lambda: KeyValueStore('cookie') # cookie_token -> user_id
# create connection to user table referenced by userid.
kv_user = lambda userid: KeyValueStore('user:' + userid)


def authorize_google(access_token):
    '''
    if user has been authorized, i.e. obtained access token,
        return user_id
    otherwise, return None
    '''
    record = kv_auth_google()[access_token]
    if record and not record['expired']:
        return record['userid']


def userid_by_googleid(googleid):
    '''
    get unique userid through its corresponding googleid.
    '''
    return kv_user_google()[googleid]


def create_user_from_google(googleid, name, email, access_token, **kwargs):
    '''
    given google credential informations such as id, access_token, name, etc.
    create a user account in our database.
    create userid = [service] + [userid@service]
    return allocated userid
    '''
    print '[creating user]'
    userid = base64.urlsafe_b64encode(hashlib.md5('google-' + googleid).hexdigest())
    kv_user_google()[googleid] = userid
    kv_auth_google()[access_token] = dict(userid=userid, expired=False)
    kv_user(userid).update(dict(
        name=name,
        email=email,
        accounts=dict(
            google=dict(id=googleid, access_token=access_token)
        )
    ))
    kv_user(userid).update(kwargs)
    return userid


def userid_by_cookie(cookie_token):
    userid = kv_cookie()[cookie_token]
    return userid


def user_by_id(userid):
    if userid:
        return kv_user(userid)


def user_by_cookie(cookie_token):
    userid = userid_by_cookie(cookie_token)
    return user_by_id(userid)


def update_user_cookie(cookie_token, userid):
    kv_cookie()[cookie_token] = userid


def remove_cookie(cookie_token):
    print '[removing cookie]', cookie_token
    kv_cookie().remove(cookie_token)


def all_tags(userid):
    tags = kv_user(userid)['tags']
    if not tags:
        return []
    return tags


def merge_tags(userid, new_tags):
    """ merge new_tags into existing tags
    """
    tags = set(all_tags(userid))
    tags = tags.union(set(new_tags))
    kv_user(userid)['tags'] = list(tags)

