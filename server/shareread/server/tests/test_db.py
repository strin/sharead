from ..db import (update_inverted_index, filter_by_inverted_index,
                  MiscInfo, KeyValueStore, DB_FILE_NAME)
import os

def test_inverted_index():
    if os.path.exists(DB_FILE_NAME):
        os.remove(DB_FILE_NAME)
    update_inverted_index(["icml'15", 'bayesian inference'], '2lkjv2h0f2903')
    update_inverted_index(["icml'15", 'topic models'], 'xh0f2903')
    update_inverted_index(["uai", 'topic models'], '2lsdklfj2h0f2903')
    update_inverted_index(["uai", 'topic models', 'max-margin'], 'jzsdklfj2h0f2903')
    result = filter_by_inverted_index(['topic models', 'uai'])
    assert result == set(['jzsdklfj2h0f2903', '2lsdklfj2h0f2903'])

def test_meta_info():
    if os.path.exists(DB_FILE_NAME):
        os.remove(DB_FILE_NAME)
    print DB_FILE_NAME
    misc = MiscInfo()
    print misc.all_tags
    assert not misc.all_tags
    tag_values = [u'icml', u'nips']
    misc.all_tags = tag_values
    assert misc.all_tags == tag_values


def test_kv_store():
    '''
    test a key value store.
    '''
    if os.path.exists(DB_FILE_NAME):
        os.remove(DB_FILE_NAME)
    kv = KeyValueStore('test')
    kv['x'] = 1
    assert kv['x'] == 1
    kv['x'] = 2
    assert kv['x'] == 2
    kv.remove('x')
    kv.remove('x')
    assert 'x' not in kv


