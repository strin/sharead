import shareread.storage.local as store

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
    def create_thumbnail(filehash):
        with open('cache/temp.pdf', 'w') as pdf_stream:
            file_stream = store.get_file(store.TEST_ACCESS_TOKEN, 'paper/' + filehash)
            pdf_stream.write(file_stream.read())
        with Image(filename="cache/temp.pdf[0]") as image:
            height_desired = 250
            width = int(height_desired * image.width / image.height)
            image.resize(width, height_desired)
            image.save(filename='cache/thumbnail.png')
        with open('cache/thumbnail.png', 'r') as thumb_stream:
            thumb_path = 'thumb/' + filehash + '.png'
            store.put_file(store.TEST_ACCESS_TOKEN, thumb_path, thumb_stream)
        return thumb_path

    def get_thumbnail(thumb_path):
        return store.get_file(store.TEST_ACCESS_TOKEN, thumb_path).read()

except ImportError as e:
    print 'ImportError', e.message
    def create_thumbnail(filehash):
        return ''

    def get_thumbnail(thumb_path):
        return ''

