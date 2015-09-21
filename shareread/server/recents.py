from shareread.server.db import (get_recent_entries, get_file_entry)

RECENTS_ADD = 'RECENTS_ADD'
RECENTS_DELETE = 'RECENTS_DELETE'
RECENTS_UPDATE = 'RECENTS_UPDATE'

def fetch_num_activities(num_fetch):
    # first pass: fetch filehashes in order.
    filehashes = get_recent_entries(num_fetch)
    return {
        'filehashes':filehashes,
    }


