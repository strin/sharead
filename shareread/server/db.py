# database utils for server.
import sqlite3 as sql
import base64
from datetime import datetime

DB_FILE_NAME = 'shareread.sqlite'

class DBConn(object):
    def __enter__(self):
        conn = sql.connect(DB_FILE_NAME)
        conn.row_factory = sql.Row
        conn.execute("""CREATE TABLE IF NOT EXISTS meta
                    (filehash text,
                    filename text,
                    fileext text,
                    upload_date text,
                    thumb_path text)
                    """)
        conn.execute("""CREATE TABLE IF NOT EXISTS recents
                    (filehash text,
                     action_type text,
                     action_date text)
                    """)
        conn.commit()
        self.conn = conn
        return conn

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

def encode_db_string(text):
    if not text:
        return text
    # return base64.b64encode(text)
    return text.replace('\'', '\'\'')

def decode_db_string(code):
    if not code:
        return code
    # return base64.b64decode(code)
    return text.replace('\'\'', '\'')

def get_recent_entries(num_entries):
    """
    use DBConn to get num_entries of recent entries
    return filehashes reversely oredered in time
    """
    filehashes = []
    filehash_set = set()
    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM recents order by rowid DESC
                       """)
        row = cursor.fetchone()
        while len(filehashes) < num_entries and row:
            filehash = row['filehash']
            if filehash not in filehash_set:
                filehashes.append(filehash)
                filehash_set.add(filehash)
            row = cursor.fetchone()
    return filehashes

def add_recent_entry(filehash, action_type, action_date = None):
    """
    use DBConn to add a file entry action to recents
    Parameter
    ======
        filehash
        action_type: recents.RECENTS_ADD, recents.RECENTS_DELETE, recents.RECENTS_UPDATE
        action_date: date of last operation, default - current time.
    """
    if not action_date:
        action_date = str(datetime.now())
    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       INSERT INTO recents (filehash, action_date, action_type) values
                       ('%(filehash)s', '%(action_date)s', '%(action_type)s')
                       """ % dict(filehash=filehash, action_date=action_date,
                                  action_type=action_type))
        conn.commit()

def get_file_entry(filehash):
    """
    use DBConn to get a file entry by filehash.
    Parameter
    ======
        filehash
    """
    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM meta WHERE filehash='%(filehash)s'
                       """ % dict(filehash=filehash)
                       )
        row = cursor.fetchone()
        if row:
            return dict(row)
    return None

def update_file_entry(filehash, filename, fileext = '', upload_date = '', thumb_path=''):
    """
    use DBConn to update/insert a file entry
    Parameter
    ========
        filehash: hash of the file, should be unique for each file
        filename: filename that describes the file
        fileext: file extension
        upload_date: date of upload.
    """
    filename = encode_db_string(filename)
    fileext = encode_db_string(fileext)
    upload_date = encode_db_string(upload_date)
    thumb_path = encode_db_string(thumb_path)

    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM meta WHERE filehash='%(filehash)s'
                       """ % dict(filehash=filehash))
        if cursor.fetchone(): # update entry if exists.
            cursor.execute("""
                        UPDATE meta
                        SET filename='%(filename)s'
                        WHERE filehash='%(filehash)s'
                        """ % dict(filehash=filehash,
                                   filename=filename)
                        )
        else: # insert new entry if not exists.
            cursor.execute("""
                        INSERT INTO meta (filehash, filename, fileext, upload_date, thumb_path) values
                        ('%(filehash)s', '%(filename)s', '%(fileext)s', '%(upload_date)s', '%(thumb_path)s')
                        """ % dict(filehash=filehash,
                                   filename=filename,
                                   fileext=fileext,
                                   upload_date=upload_date,
                                   thumb_path=thumb_path)
                        )
