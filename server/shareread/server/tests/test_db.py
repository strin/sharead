import shareread.server.db as db
db.set_testing_mode()

from shareread.server.userfile import (create_file_entry, update_file_entry, get_file_entry,
                                       add_recent_entry, update_inverted_index, filter_by_inverted_index,
                                       RECENTS_ADD, RECENTS_UPDATE, fetch_num_activities)
from shareread.server.user import (user_by_cookie, authorize_google, userid_by_cookie,
                                   create_user_from_google, update_user_cookie,
                                   remove_cookie, user_by_id, all_tags, merge_tags)
import os


def test_inverted_index():
    db.flush_db()
    userid = '1'
    update_inverted_index(userid, ["icml'15", 'bayesian inference'], '2lkjv2h0f2903')
    update_inverted_index(userid, ["icml'15", 'topic models'], 'xh0f2903')
    update_inverted_index(userid, ["uai", 'topic models'], '2lsdklfj2h0f2903')
    update_inverted_index(userid, ["uai", 'topic models', 'max-margin'], 'jzsdklfj2h0f2903')
    result = filter_by_inverted_index(userid, ['topic models', 'uai'])
    assert result == set(['jzsdklfj2h0f2903', '2lsdklfj2h0f2903'])


