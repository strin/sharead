# metadata extraction with mendeley API.
import urllib2
from pprint import pprint
import json

ACCESS_TOKEN = 'MSwxNDY2NTUwOTEwNzQxLDE2MTM1MjgzLDMyNDksYWxsLCwsMGE4My02YWU5Y2Y0NzU1MWQ5NmY5MjQxZTk3YmY3YjY1YWRlMzQwMCxiOGQyMzE1Ni05M2NjLTM2ZDUtYmI0OS01OWJlOTZlOTIxYTAsQ0FDeEtnQVppdHNSSE1XUEFsVEJlYkJVMjI4'


def extract_metadata_from_pdf(stream):
    stream.seek(0)
    request = urllib2.Request('https://api.mendeley.com/documents',
                              data=stream.read(),
                              headers={
                                  'Authorization': 'Bearer %s' % ACCESS_TOKEN,
                                  'Content-Type': 'application/pdf',
                                  'Content-Disposition': 'attachment; filename="example.pdf"'
                              })
    resp = urllib2.urlopen(request).read()
    result = json.loads(resp)
    result['title'] = result['title'].title() # convert to same title format.
    return result

