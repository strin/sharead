import shareread.storage as store
import shareread.storage.local as local_store
from shareread.utils import mkdir_if_necessary
from os import path

def parse_webkitform(request_body):
    """
    Given the request body, this method parses the submitted webkit form.

    Input:
        request_body (str)

    Output:
        a dict with the following keys
            data: the data submitted
            boundary: a pair of webkit form boundaries.
            Content-Disposition
            Content-Type
    """
    request_lines = request_body.split('\r\n')
    boundary = (request_lines[0], request_lines[-2])
    content_disposition = request_lines[1]
    content_type = request_lines[2]
    data = '\r\n'.join(request_lines[4:-2])
    try:
        filename = content_disposition.split(';')[-1].split('=')[-1]
        filename = filename.strip()[1:-1]
    except:
        filename = 'untitled'
    return {
        "data": data,
        "boundary": boundary,
        "Content-Disposition": content_disposition,
        "Content-Type": content_type,
        "filename": filename
    }

def parse_filename(filename):
    """
    Given a filename, parse the name and ext
    Return (filename, ext)
    """
    dot_pos = filename.rfind('.')
    if dot_pos == -1:
        ext = ""
    else:
        ext = filename[dot_pos+1:]
        filename = filename[:dot_pos]
    return (filename, ext)

try:
    from wand.image import Image
    def create_thumbnail(local_pdf_abspath, local_thumb_abspath):
        mkdir_if_necessary(path.dirname(local_thumb_abspath))
        with Image(filename="%s[0]" % local_pdf_abspath) as image:
            height_desired = 250
            width = int(height_desired * image.width / image.height)
            image.resize(width, height_desired)
            image.save(filename=local_thumb_abspath)


    def get_thumbnail_path(filehash):
        return 'thumb/' + filehash + '.png' # .png make sure an image is saved.


except ImportError as e:
    print 'ImportError', e.message
    def create_thumbnail(filehash):
        return ''

    def get_thumbnail_path(thumb_path):
        return ''

