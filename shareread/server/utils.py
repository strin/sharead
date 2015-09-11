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

