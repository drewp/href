import lxml.html.soupparser
import datetime, socket
from dateutil.tz import tzlocal
import restkit

class CantGetTitle(ValueError):
    pass

class PageTitle(object):
    def __init__(self, db):
        self.coll = db['pageTitle']

    def getPageTitleNow(self, uri):
        try:
            response = restkit.request(uri, timeout=1, follow_redirect=True,
                                headers={
                                    'user-agent':
                                    'link title checker - drewp@bigasterisk.com'
                                })
            if not response.status.startswith('2'):
                raise CantGetTitle("(got %s)" % response.status)
            root = lxml.html.soupparser.fromstring(
                response.body_string())

            for title in root.cssselect("title"):
                return title.text
        except restkit.RequestError:
            raise CantGetTitle("(error requesting title from site)")
            
    def pageTitle(self, uri):
        """page title from our db or by getting a new load from the page"""
        doc = self.coll.find_one({'_id' : uri})
        if doc is None:
            try:
                title = self.getPageTitleNow(uri)
            except CantGetTitle, e:
                return str(e)
            doc = {'_id': uri, 'title' : title,
                   'getTime':datetime.datetime.now(tzlocal())}
            self.coll.insert(doc, safe=True)
        return doc['title']
