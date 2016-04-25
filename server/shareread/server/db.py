# database utils for server.
import sqlite3 as sql
import base64
import json
from datetime import datetime

DB_FILE_NAME = 'shareread.sqlite'

class DBConn(object):
    def __enter__(self):
        conn = sql.connect(DB_FILE_NAME)
        conn.row_factory = sql.Row
        # create the file metadata table.
        conn.execute("""CREATE TABLE IF NOT EXISTS meta
                    (filehash text,
                    filename text,
                    fileext text,
                    upload_date text,
                    thumb_path text,
                    tags text)
                    """)
        # create the recents table.
        conn.execute("""CREATE TABLE IF NOT EXISTS recents
                    (filehash text,
                     action_type text,
                     action_date text)
                    """)
        # create the table for inverted indexing.
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS inverted
                     (tag text PRIMARY KEY,
                     filehashes text)
                     """)
        # create the table for some global info.
        conn.execute("""
                     CREATE TABLE IF NOT EXISTS info
                     (key text PRIMARY KEY,
                     value text)
                     """)
        conn.commit()
        self.conn = conn
        return conn

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

class MiscInfo(object):
    def _fetch_row(self):
        with DBConn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                           SELECT * FROM info WHERE key='tags'
                           """)
            row = cursor.fetchone()
            return row


    @property
    def all_tags(self):
        row = self._fetch_row()
        if row:
            return json.loads(row['value'])
        return []


    @all_tags.setter
    def all_tags(self, tags):
        value = json.dumps(tags)
        with DBConn() as conn:
            cursor = conn.cursor()
            if self._fetch_row():
                cursor.execute("""
                               UPDATE info
                               SET value=:value
                               WHERE key='tags'
                               """, dict(value=value))
            else:
                cursor.execute("""
                               INSERT INTO info
                               (key, value)
                               VALUES
                               ('tags', :value)
                               """, dict(value=value))

    def merge_tags(self, new_tags):
        """ merge new_tags into existing tags
        """
        tags = set(self.all_tags)
        tags = tags.union(set(new_tags))
        self.all_tags = list(tags)

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
    def decode_meta(row):
        if not row:
            return row
        meta = dict(row)
        if 'tags' in meta:
            meta['tags'] = json.loads(meta['tags'])
        return meta

    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM meta WHERE filehash='%(filehash)s'
                       """ % dict(filehash=filehash)
                       )
        row = cursor.fetchone()
        return decode_meta(row)
    return None

def update_file_entry(filehash, **kwargs):
    """
    use DBConn to update a file entry incrementally.
    Parameter
    =========
    filehash: required, to identify the file entry
    kwargs: a dict of key-value modifications.
    """
    # allowed modifications keys.
    whitelist = set([
        "filename",
        "fileext",
        "tags",
        "upload_date"
        "thumb_path"
    ])
    def encode_meta(key, value):
        if key == "tags": # use json encoding.
            return json.dumps(value)
        return encode_db_string(value)
    # merge into global tags.
    if 'tags' in kwargs:
        MiscInfo().merge_tags(kwargs['tags'])

    kwargs = {key: encode_meta(key, value)
              for (key, value) in kwargs.items() if key in whitelist}
    update_lang = ','.join(map(lambda key: key + "='%(" + key + ")s'",
                               kwargs.keys()))
    update_lang = """
                    UPDATE meta
                    SET %(update_lang)s
                    WHERE filehash='%(filehash)s'
                  """ % dict(update_lang=update_lang,
                             filehash=filehash)
    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute(update_lang % kwargs)

def create_file_entry(filehash, filename, fileext = '',
                      upload_date = '', thumb_path='', tags=[]):
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
    # merge into global tags.
    MiscInfo().merge_tags(tags)
    tags = encode_db_string(json.dumps(tags))

    with DBConn() as conn:
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT * FROM meta WHERE filehash='%(filehash)s'
                       """ % dict(filehash=filehash))
        data = dict(filehash=filehash,
                    filename=filename,
                    fileext=fileext,
                    upload_date=upload_date,
                    thumb_path=thumb_path,
                    tags=tags)
        if cursor.fetchone(): # update entry if exists.
            cursor.execute("""
                        UPDATE meta
                        SET filename='%(filename)s',
                            fileext='%(fileext)s',
                            upload_date='%(upload_date)s',
                            thumb_path='%(thumb_path)s',
                            tags='%(tags)s'
                        WHERE filehash='%(filehash)s'
                        """ % data)
        else: # insert new entry if not exists.
            cursor.execute("""
                        INSERT INTO meta
                           (filehash,
                           filename,
                           fileext,
                           upload_date,
                           thumb_path,
                           tags)
                        VALUES
                            ('%(filehash)s',
                           '%(filename)s',
                           '%(fileext)s',
                           '%(upload_date)s',
                           '%(thumb_path)s',
                           '%(tags)s')
                        """ % data)

def update_inverted_index(tags, filehash):
    """
    use DBConn to update the inverted index table
    """
    with DBConn() as conn:
        cursor = conn.cursor()
        for tag in tags:
            #tag = encode_db_string(tag)
            cursor.execute("""
                        SELECT * FROM inverted
                           WHERE tag=:tag
                        """, dict(tag=tag))
            result = cursor.fetchone()
            if result:
                filehashes = json.loads(result['filehashes'])
                filehashes.append(filehash)
                cursor.execute("""
                               UPDATE inverted
                               SET filehashes=:filehashes
                               WHERE tag=:tag
                               """,
                               dict(tag=tag, filehashes=json.dumps(filehashes)))
            else:
                filehashes = [filehash]
                cursor.execute("""
                               INSERT INTO inverted
                               (tag, filehashes)
                               VALUES
                               (:tag, :filehashes)
                               """, dict(tag=tag, filehashes=json.dumps(filehashes)))

def filter_by_inverted_index(tags):
    """
    use DBConn to filter the filehashes based on the tags given
    """
    result = None
    with DBConn() as conn:
        cursor = conn.cursor()
        for tag in tags:
            cursor.execute("""
                            SELECT * FROM inverted
                            WHERE tag=:tag
                            """, dict(tag=tag))
            row = cursor.fetchone()
            if row:
                filehash_set = set(json.loads(row['filehashes']))
                result = result.intersection(filehash_set) if result else filehash_set
    return result if result else set()

