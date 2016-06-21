# stores metadata about pdf files.
from shareread.server.db import KeyValueStore, SortedList

kv_paper = lambda filehash: KeyValueStore('paper:' + filehash)


def save_paper_entry(filehash, metadata):
    kv_paper(filehash).update(metadata)


def get_paper_entry(filehash):
    return kv_paper(filehash).mget([
        'title', 'authors', 'abstract'
    ])

