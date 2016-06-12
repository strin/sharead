# convert pdf to html for efficient rendering.
import shareread.storage.local as store_local
import shareread.storage as store
from shareread.utils import mkdir_if_necessary
from os import system, path, environ

if 'PDF2HTML' in environ:
    PDF2HTML = environ.get('PDF2HTML')
else:
    PDF2HTML = 'pdf2htmlEX' # pdf2html binary path.


def get_rendered_path(filehash):
    return store_local.get_local_path(store_local.TEST_ACCESS_TOKEN, 'render/' + filehash)


def render_html_from_pdf(filehash, pdf_stream):
    '''
    supposely every pdf has a unique hash.
    this function creates a html view of <filehash>, and store it under rendered/<filehash>
    '''
    pdf_stream.seek(0)
    local_pdf_path = 'render/pdf/' + filehash
    local_html_path = 'render/html/' + filehash
    local_pdf_abspath = store_local.get_local_path(store_local.TEST_ACCESS_TOKEN, local_pdf_path)
    local_html_abspath = store_local.get_local_path(store_local.TEST_ACCESS_TOKEN, local_html_path)

    mkdir_if_necessary(path.dirname(local_pdf_abspath))
    mkdir_if_necessary(path.dirname(local_html_abspath))

    store_local.put_file(store_local.TEST_ACCESS_TOKEN, local_pdf_path, pdf_stream)
    system('%(pdf2html)s --zoom 1 --process-outline 0 %(pdf)s %(html)s' %
            dict(pdf2html=PDF2HTML,
                 pdf=local_pdf_abspath,
                 html=local_html_abspath
              )
        )

    html_path = 'render/' + filehash

    with open(local_html_abspath, 'rb') as html_stream:
        store.put_file(store.TEST_ACCESS_TOKEN, html_path, html_stream)
