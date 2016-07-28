# stores metadata about pdf files.
from shareread.server.db import KeyValueStore, SortedList
import time
import json
from multiprocessing import Process

kv_paper = lambda filehash: KeyValueStore('paper:' + filehash)
kv_url_paper = lambda: KeyValueStore('paperurl') # store paper pined from urls.


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


def inverse_indexing_once():
    kv_paperwords = lambda filehash: KeyValueStore('paperwords:' + filehash)
    scopes = KeyValueStore.scopes('paper:*')
    from nltk.tokenize import TweetTokenizer
    tokenizer = TweetTokenizer()
    def make_dict(text, weight=1., prefix_weight=0.):
        if not text:
            return {}
        words = tokenizer.tokenize(text.lower().strip())
        result = {}
        for word in words:
            for i in range(1, len(word)):
                prefix = word[:i]
                if prefix not in result:
                    result[prefix] = 0.
                result[prefix] += prefix_weight
            result[word] += weight
        return result

    def merge_dict(dict1, dict2):
        new_dict = {}
        for word in set(dict1.keys()).union(dict2.keys()):
            weight1 = dict1.get(word, 0.)
            weight2 = dict2.get(word, 0.)
            new_dict[word] = weight1 + weight2
        return new_dict

    for scope in scopes:
        filehash = scope[len('paper:'):]
        meta = KeyValueStore(scope_name=scope)
        title = meta['title']
        abstract = meta.get('abstract', default='')

        dict_title = make_dict(title, weight=6., prefix_weight=0.06)
        dict_abstract = make_dict(abstract, weight=2., prefix_weight=0.02)
        final_dict = merge_dict(dict_title, dict_abstract)

        authors = meta['authors']
        print authors
        if authors:
            print authors
            for author in authors:
                dict_author = make_dict(author['first_name'] + ' ' + author['last_name'])
                final_dict = merge_dict(dict_author, final_dict)

        kv_paperwords(filehash).update(final_dict)


def inverse_indexing_process():
    count = 0
    print_freq = 100
    while True:
        inverse_indexing_once()
        count += 1
        if count % print_freq == 0:
            print '[inverse indexing] updated %d times' % print_freq
        time.sleep(1.)


class InverseIndexingProcess(object):
    '''
    manage inverse indexing background process.
    '''
    def __init__(self):
        self.process = Process(target=inverse_indexing_process)


    def start(self):
        self.process.daemon = True # killed when parent dies.
        self.process.start()


    def join(self):
        self.process.join()






def rank_by_inverted_words(raw_query, filehashes=None):
    from nltk.tokenize import TweetTokenizer
    tokenizer = TweetTokenizer()
    keywords = tokenizer.tokenize(raw_query)

    kv_paperwords = lambda filehash: KeyValueStore('paperwords:' + filehash)
    if not filehashes: # retrieve all from db. complexity warning.
        scopes = KeyValueStore.scopes('paper:*')
        filehashes = [scope[len('paper:'):] for scope in scopes]

    score_by_filehash = {}
    for filehash in filehashes:
        word_dict = kv_paperwords(filehash)
        score = 0.
        for word in keywords:
            score += word_dict.get(word, default=0.)
        score_by_filehash[filehash] = score
    print score_by_filehash
    return sorted(score_by_filehash, key=lambda k: score_by_filehash[k], reverse=True)

