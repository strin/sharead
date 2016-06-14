# store files at local server
import sys
import os
from datetime import datetime
from shareread.utils import mkdir_if_necessary

ACCESS_TOKEN = 'strin'

def _get_access_token():
    return str(datetime.now())

def get_local_path(path):
    return os.path.join('upload', ACCESS_TOKEN, path)

def put_file(path, stream):
    local_path = get_local_path(ACCESS_TOKEN, path)
    mkdir_if_necessary(os.path.dirname(local_path))
    with open(local_path, 'w') as f:
        f.write(stream.read())

def get_file(path):
    local_path = get_local_path(ACCESS_TOKEN, path)
    return open(local_path, 'r')

def get_url(path):
    return get_local_path(path)

