# stores metadata about pdf files.
from shareread.server.db import KeyValueStore, SortedList

kv_paper = lambda filehash: KeyValueStore('paper:' + filehash)
kv_url_paper = lambda: KeyValueStore('paper:url') # store paper pined from urls.


def save_paper_entry(filehash, metadata):
    kv_paper(filehash).update(metadata)


def get_paper_entry(filehash):
    return kv_paper(filehash).mget([
        'title', 'authors', 'abstract'
    ])


def save_paper_url(url, filehash):
    kv_url_paper()[url] = filehash


def get_filehash_by_url(url):
    return kv_url_paper()[url]
