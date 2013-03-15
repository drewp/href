#!bin/python
"""
serve some queries over bookmarks:

/user
/user/tag+tag+tag

and the add-bookmark stuff

"""
import pymongo, bottle, time, urllib, datetime, json, restkit
from collections import defaultdict
from urllib2 import urlparse
from dateutil.tz import tzlocal
from bottle import static_file
from jadestache import Renderer
from pagetitle import PageTitle
from link import Links, NotFound
db = pymongo.Connection('bang', tz_aware=True)['href']
pageTitle = PageTitle(db)
links = Links(db)
renderer = Renderer(search_dirs=['template'], debug=bottle.DEBUG)

siteRoot = 'https://bigasterisk.com/href'

def getLoginBar():
    openidProxy = restkit.Resource("http://bang:9023/")
    return openidProxy.get("_loginBar",
                 headers={"Cookie" : bottle.request.headers.get('cookie')}).body_string()

def getUser():
    agent = bottle.request.headers.get('x-foaf-agent', None)
    username = db['user'].find_one({'_id':agent})['username'] if agent else None
    return username, agent
    
@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

def recentTags(user, tags=None):
    out = {'links':[]}
    t1 = time.time()
    spec = {'user':user}
    if tags:
        spec['extracted.tags'] = {'$all' : tags}
    for doc in db['links'].find(spec, sort=[('t', -1)], limit=50):
        out['links'].append(links.forDisplay(doc))
    out['stats'] = {'queryTimeMs' : round((time.time() - t1) * 1000, 2)}
    return out

def allTags(user, withTags=[]):
    """withTags limits results to other tags that have been used with
    those tags"""
    withTags = set(withTags)
    count = defaultdict(lambda: 0) # tag : count
    for doc in db['links'].find({'user':user}, fields=['extracted.tags']):
        docTags = set(doc.get('extracted', {}).get('tags', []))
        if withTags and not withTags.issubset(docTags):
            continue
        for t in docTags.difference(withTags):
            count[t] = count[t] + 1
    byFreq = [(n, t) for t,n in count.iteritems()]
    byFreq.sort(key=lambda (n,t): (-n, t))
    return [{'label': t, 'count': n} for n, t in byFreq]
    
def renderWithTime(name, data):
    t1 = time.time()
    rendered = renderer.render_name(name, data)
    dt = (time.time() - t1) * 1000
    rendered = rendered.replace('TEMPLATETIME', "%.02f ms" % dt)
    return rendered
    
@bottle.route('/addLink')
def addLink():
    out = {
        'toRoot':  '.',
        'absRoot': siteRoot,
        'user': getUser()[0],
        'withKnockout':  True,
        'fillHrefJson':  json.dumps(bottle.request.params.get('url', '')),
        'loginBar':  getLoginBar(),
    }
    return renderWithTime('add.jade', out)

@bottle.route('/addOverlay')
def addOverlay():
    p = bottle.request.params

    return ""

    
@bottle.route('/addLink/proposedUri')
def proposedUri():
    uri = bottle.request.params.uri
    user, _ = getUser()

    try:
        prevDoc = links.find(uri)
    except NotFound:
        prevDoc = None
    
    return {
        'description': prevDoc['description'] if prevDoc else pageTitle.pageTitle(uri),
        'tag' : prevDoc['tag'] if prevDoc else '',
        'extended' : prevDoc['extended'] if prevDoc else '',
        'shareWith' : prevDoc.get('shareWith', []) if prevDoc else [],
        'suggestedTags': ['tag1', 'tag2'],
        'existed': prevDoc is not None,
        }

if 0:
    pass#proposal check existing links, get page title (stuff that in db), get tags from us and other serviecs. maybe the deferred ones ater


@bottle.route('/tags')
def tagFilterComplete():
    params = bottle.request.params
    haveTags = filter(None, params['have'].split(','))
    return {'tags' : [
        {'id': t['label'],
         'text': "%s (%s%s)" % (t['label'], t['count'], " left" if haveTags else "")}
        for t in allTags(params.user,
                         withTags=haveTags)]}
    
@bottle.route('/<user>/')
def userSlash(user):
    bottle.redirect("/%s" % urllib.quote(user))
    
@bottle.route('/<user>', method='GET')
def userAll(user):
    return userLinks(user, "", toRoot=".")

@bottle.route('/<user>', method='POST')
def userAddLink(user):
    if getUser()[0] != user:
        raise ValueError("not logged in as %s" % user)
    print repr(bottle.request.params.__dict__)
    doc = links.fromPostdata(bottle.request.params,
                             user,
                             datetime.datetime.now(tzlocal()))
    links.insertOrUpdate(doc)

    print "notify about sharing to", repr(doc['shareWith'])
        
    bottle.redirect(siteRoot + '/' + user)
    
@bottle.route('/<user>/<tags>')
def userLinks(user, tags, toRoot=".."):
    tags = filter(None, tags.split('+'))
    data = recentTags(user, tags)
    data['loginBar'] = getLoginBar()
    data['desc'] = ("%s's recent links" % user) + (" tagged %s"  % (tags,) if tags else "")
    data['toRoot'] = toRoot
    data['allTags'] = allTags(user)
    data['user'] = user

    data['pageTags'] = [{"word":t} for t in tags]
    data['stats']['template'] = 'TEMPLATETIME'
    return renderWithTime('links.jade', data)
    
@bottle.route('/')
def root():
    data = {
        'loginBar': getLoginBar(),
        'toRoot': ".",
        'stats': {'template': 'TEMPLATETIME'},
        'users': [{'user':doc['username']} for doc in db['user'].find()],
        }
    return renderWithTime('index.jade', data)
    
if __name__ == '__main__':
    bottle.run(server='gunicorn', host='0.0.0.0', port=10002, workers=4)
