
class NotFound(ValueError):
    pass

class Links(object):
    def __init__(self, db):
        self.coll = db['links']
        
    def insertOrUpdate(self, doc):
        self.extract(doc)
        self.coll.update({'href':doc['href']}, doc, upsert=True, safe=True)

    def extract(self, doc):
        forUsers = []
        tags = []
        for t in doc.get('tag', '').split(' '):
            if t.startswith('for:'):
                forUsers.append(t[4:])
            else:
                tags.append(t)
        doc['extracted'] = dict(tags=tags, forUsers=forUsers)

    def find(self, uri):
        docs = list(self.coll.find({'href': uri}))
        if len(docs) == 0:
            raise NotFound("not found")
        elif len(docs) > 1:
            raise ValueError("%s docs found for href %s" % (len(docs), uri))
        else:
            return docs[0]
            
