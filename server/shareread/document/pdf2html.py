# convert pdf to html for efficient rendering.
import shareread.storage.local as store
from shareread.utils import mkdir_if_necessary
from os import system, path, environ

if 'PDF2HTML' in environ:
    PDF2HTML = environ.get('PDF2HTML')
else:
    PDF2HTML = 'pdf2htmlEX' # pdf2html binary path.
RENDER_ROOT = 'rendered'

def get_rendered_path(filehash):
    '''
    given document filehash, determine the path to rendered html
    '''
    mkdir_if_necessary(RENDER_ROOT)
    return path.join(RENDER_ROOT, filehash)


def render_html_from_pdf(filehash):
    '''
    supposely every pdf has a unique hash.
    this function creates a html view of <filehash>, and store it under rendered/<filehash>
    '''
    system('%(pdf2html)s --zoom 1 --process-outline 0 %(pdf)s %(html)s' %
            dict(pdf2html=PDF2HTML,
                 pdf=store.get_local_path(store.TEST_ACCESS_TOKEN, filehash),
                 html=get_rendered_path(filehash)
              )
        )
