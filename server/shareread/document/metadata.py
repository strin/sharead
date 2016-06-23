# metadata extraction with mendeley API.
import urllib2
import requests
from requests.auth import HTTPBasicAuth
from pprint import pprint
import json
from StringIO import StringIO
import string
import base64


CLIENT_ID = '3254'
CLIENT_SECRET = 'R2F8ZhRkAud4ga95'
ACCESS_TOKEN = 'MSwxNDY2NjI0ODM4ODY3LDE2MTM1MjgzLDMyNTQsYWxsLCwsODM0Ny0zYmEzZTY5NzU1MTVmNjk5N2I1LWE0NDhhMjE1ZDJkMGIzYzUsYjhkMjMxNTYtOTNjYy0zNmQ1LWJiNDktNTliZTk2ZTkyMWEwLDg1MmJxNkhSTk84OVJOUHJXRUYwRHo2TlFmaw'
REFRESH_TOKEN = 'MSwxNjEzNTI4MywzMjU0LGFsbCwwN2Y1NzNiNDA1OTc1NTE5ODE5MzY0MTNjYzhjMWY1OTg2MTc0YmEsNzdmNTczYjQwNTk3NTUxOTgxOTM2NDEzY2M4YzFmNTk4NjE3NGJhLDE0NjY2MjEzMzE3OTgsYjhkMjMxNTYtOTNjYy0zNmQ1LWJiNDktNTliZTk2ZTkyMWEwLEJOdnRZaHdwUWZKMm5Zd0tCYTMwdkhVN2hTcw'
REDIRECT_URI = 'sharead.org%2Foauth%2Fmendeley'


def extract_metadata_from_pdf(data):
    stream = StringIO(data)
    # get access token using refresh token.
    resp = requests.post('https://api.mendeley.com/oauth/token',
                              data=('grant_type=refresh_token&refresh_token=%s'
                                    '&redirect_uri=%s'
                                    % (REFRESH_TOKEN, REDIRECT_URI)),
                              headers={
                                  'Content-Type': 'application/x-www-form-urlencoded'
                              },
                              auth=HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)
                        ).json()
    access_token = resp['access_token']
    # assert(resp['refresh_token'] == REFRESH_TOKEN)
    # use access token to request paper metadata.
    result = requests.post('https://api.mendeley.com/documents',
                            data=stream.read(),
                            headers={
                                'Authorization': 'Bearer %s' % access_token,
                                'Content-Type': 'application/pdf',
                                'Content-Disposition': 'attachment; filename="example.pdf"'
                            }).json()
    result['title'] = string.capwords(result['title']) # convert to same title format.
    return result

