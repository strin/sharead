# store files at local server
import sys
import os
from datetime import datetime

TEST_ACCESS_TOKEN = str(datetime.now())

def _get_access_token():
    return str(datetime.now())

def mkdir_if_necessary(path):
    dirpath = os.path.dirname(path)
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

def get_local_path(access_token, path):
    return os.path.join('upload', access_token, path)

def put_file(access_token, path, stream):
    local_path = get_local_path(access_token, path)
    mkdir_if_necessary(local_path)
    with open(local_path, 'w') as f:
        f.write(stream.read())

def get_file(access_token, path):
    local_path = get_local_path(access_token, path)
    return open(local_path, 'r')

