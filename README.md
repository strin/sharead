# ShareRead 

<img src='https://travis-ci.com/strin/sharead.svg?token=1QXsyhqe3sEcnJSezGLL&branch=mvp0.2'></img>

A collaborative paper reading experience that integrates paper reading, management and sharing in one place. 

## MVP V0.2

The goal for MVP V0.2 is to build a collaborative reader, where people can save and share papers. Here are the planned features:

* [ ] User management. 
* [ ] Collaborative PDF Reader.
* [ ] Paper metadata extraction.
* [ ] Continuous testing and deploying.
* [ ] Some minor feature requests.

## MVP V0.1
<img src="http://g.recordit.co/fYNJiDDQqu.gif"></img>

## Setting up Development Environment

At project root:

```
virtualenv my-venv
source my-venv/bin/activate
sudo pip install -r requirements.txt
```

To set up testing environment (use fake redisdb etc.), change `__builtin__.testmode = lambda: False` to `True` in server.py. Then `python server.py` to start server.

TODO(dixiao):
- ImageMagik `DYLD_LIBRARY_PATH`, `MAGICK_HOME`
- pdf2htmlEX
- To compile static files