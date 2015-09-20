from ..db import update_inverted_index, DB_FILE_NAME, filter_by_inverted_index
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



