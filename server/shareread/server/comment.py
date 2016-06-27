from shareread.server.db import KeyValueStore, SortedList

kv_threads = lambda paperid: SortedList('paper:' + paperid) # paperid -> threads
kv_comments = lambda threadid: SortedList('thread:' + threadid) # thread -> comments

# threads
# - paperid
# - threadid, used to locate all posts
# - meta data
# -- pos, position in paper (can be used for on demand loading)
# -- npost, number of posts (can be used for preview)

# comments
# - threadid
# - commentid
# - usedid
# - text
# - datetime

# get all threads given paperid
def get_threads(paperid, k=-1):
    threads = kv_threads(paperid)[-1:0]
    return threads

# get comments by threadid
def get_comments(threadid, k=-1):
    comments = kv_comments(threadid)[-1:0]
    return comments
    
# get all comments given paperid
def get_all_comments(paperid, k=-1):
    threads = get_threads(paperid)
    comments = []
    for i in threads:
        comments += get_comments(i)
    return {
        'comments':comments,
    }

# add thread
def add_thread(paperid):
    _kv_threads = kv_threads(paperid)
    threadid = len(_kv_threads)
    _kv_threads.append(dict(
        paperid=paperid,
        threadid=threadid
    ), threadid)
    return threadid

# add comment
def add_comment(paperid, userid, text, threadid = None):
    if not threadid:
        threadid = add_thread(paperid)
    _kv_comments = kv_comments(threadid)
    commentid = len(_kv_comments)
    _kv_comments.append(dict(
        threadid=threadid,
        commentid=commentid,
        userid=userid,
        text=text
    ), commentid)

# TODO(dixiao): delete comments
# delete comment
def delete_comment(paperid, threadid, userid):
    pass

# delete thread
def delete_thread(paperid, threadid, userid):
    pass