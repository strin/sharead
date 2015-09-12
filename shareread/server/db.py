# database utils for server.
import sqlite3 as sql
import base64
from datetime import datetime

DB_FILE_NAME = 'shareread.sqlite'

class DBConn(object):
    def __enter__(self):
        conn = sql.connect(DB_FILE_NAME)
        conn.execute("""CREATE TABLE IF NOT EXISTS meta
                    (filehash text,
                    filename text,
                    upload_date text)
                    """)
        conn.commit()
        self.conn = conn
        return conn

    def __exit__(self, type, value, traceback):
        self.conn.close()

def encode_db_string(text):
    if not text:
        return text
    return base64.b64encode(text)

def decode_db_string(code):
    if not code:
        return code
    return base64.b64decode(code)

def update_file_entry(filehash, filename, upload_date = None):
    """
    use DBConn to update/insert a file entry
    Parameter
    ========
        filehash: hash of the file, should be unique for each file
        filename: filename that describes the file
        upload_date: date of upload.
    """
    filename = encode_db_string(filename)
    upload_date = encode_db_string(upload_date)

    # automatically fill in missing upload date.
    if not upload_date:
        upload_date = str(datetime.now())

    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM meta WHERE filehash='%(filehash)s'
                       """ % dict(filehash=filehash))
        if cursor.fetchone(): # update entry if exists.
            cursor.execute("""
                        UPDATE meta
                        SET filename='%(filename)s', upload_date='%(upload_date)s'
                        WHERE filehash='%(filehash)s'
                        """ % dict(filehash=filehash,
                                    filename=filename,
                                    upload_date=upload_date)
                        )
        else: # insert new entry if not exists.
            cursor.execute("""
                        INSERT INTO meta (filehash, filename, upload_date) values
                        ('%(filehash)s', '%(filename)s', '%(upload_date)s')
                        """ % dict(filehash=filehash,
                                    filename=filename,
                                    upload_date=upload_date)
                        )
        conn.commit()
