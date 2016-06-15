'''
this module provides high-level functions to upload, access and retrive files.
'''
from shareread.utils import Timer
import shareread.storage as store
import shareread.storage.local as local_store
import shareread.document.pdf2html as pdf2html
from shareread.server.utils import (create_thumbnail, get_thumbnail_path)
from shareread.server.db import (create_file_entry, add_recent_entry)
from shareread.server.recents import (RECENTS_ADD)

from StringIO import StringIO
import hashlib
import base64
from datetime import datetime


def create_file(filename, ext, data):
    data_stream = StringIO(data)
    # get filehash.
    md5_code = hashlib.md5(data).digest()
    filehash = base64.urlsafe_b64encode(md5_code)
    # first, process files locally on server.
    # the server might have ephermal memory, so the files created are temporary.
    pdf_path = 'pdf/' + filehash
    local_store.put_file('upload/' + pdf_path, data_stream)
    # 1. render html
    html_path = 'html/' + filehash
    pdf2html.render_html_from_pdf(
        local_store.get_local_path('upload/' + pdf_path),
        local_store.get_local_path('upload/' + html_path)
    )
    # 2. render thumbnail.
    thumb_path = get_thumbnail_path(filehash)
    create_thumbnail(
        local_store.get_local_path('upload/' + pdf_path),
        local_store.get_local_path('upload/' + thumb_path)
    )

    # upload results to permanent storage.
    store.put_file_from_local('html/' + filehash, 'upload/' + html_path)
    store.put_file_from_local(get_thumbnail_path(filehash), 'upload/' + thumb_path)
    data_stream.seek(0)
    store.put_file('paper/' + filehash, data_stream)
    data_stream.close()

    with Timer('share urls'):
        print 'paper url', store.get_url('paper/' + filehash)
        print 'html url', store.get_url('html/' + filehash)
        print 'thumb url', store.get_url(get_thumbnail_path(filehash))
    # create html view.
    # get upload date.
    upload_date = str(datetime.now())

    # update db.
    create_file_entry(filehash, filename, ext, upload_date, thumb_path=thumb_path)
    add_recent_entry(filehash, action_type=RECENTS_ADD)
    return filehash

