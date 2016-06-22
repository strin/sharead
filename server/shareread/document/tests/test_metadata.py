# test metadata extraction.
from shareread.document.metadata import *


def test_metadata_from_pdf():
    pdf_path = 'shareread/document/tests/test.pdf'
    with open(pdf_path, 'rb') as f:
        result = extract_metadata_from_pdf(f.read())
        assert(result['title'] == 'Bitcoin: A Peer-to-peer Electronic Cash System')
        assert(result['authors'] == [{u'first_name': u'Satoshi', u'last_name': u'Nakamoto'}])

