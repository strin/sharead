# convert pdf to html for efficient rendering.
import shareread.storage.local as local_store
import shareread.storage as store
from shareread.utils import mkdir_if_necessary
from os import system, path, environ

if 'PDF2HTML' in environ:
    PDF2HTML = environ.get('PDF2HTML')
else:
    PDF2HTML = 'pdf2htmlEX' # pdf2html binary path.


def render_html_from_pdf(local_pdf_abspath, local_html_abspath):
    '''
    this function wraps pdf2html binary.
        local_pdf_abspath: the path to local temporary pdf file.
        local_html_abspath: the path to output temporary html rendering.
    '''
    mkdir_if_necessary(path.dirname(local_pdf_abspath))
    mkdir_if_necessary(path.dirname(local_html_abspath))

    system('%(pdf2html)s --zoom 1 --process-outline 0 %(pdf)s %(html)s' %
        dict(pdf2html=PDF2HTML,
             pdf=local_pdf_abspath,
             html=local_html_abspath
          )
    )


