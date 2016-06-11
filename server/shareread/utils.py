import os


def mkdir_if_necessary(dirpath):
    if not os.path.exists(dirpath):
        os.makedirs(dirpath)

