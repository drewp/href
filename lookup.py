#!bin/python
"""
serve some queries over bookmarks:

/user
/user/tag+tag+tag

and the add-bookmark stuff

"""
import pymongo, bottle, time, urllib.request, urllib.parse, urllib.error, datetime, json, logging
import requests
from collections import defaultdict
from urllib.parse import urlparse
from dateutil.tz import tzlocal
from bottle import static_file
from jadestache import Renderer
from pagetitle import PageTitle
from link import Links, NotFound
db = pymongo.Connection('mongodb.default.svc.cluster.local', tz_aware=True)['href']
pageTitle = PageTitle(db)
links = Links(db)
renderer = Renderer(search_dirs=['template'], debug=bottle.DEBUG)
log = logging.getLogger()

def getLoginBar():
    return requests.get("http://openid-proxy.default.svc.cluster.local:9023/_loginBar",
                           headers={
                               "Cookie" : bottle.request.headers.get('cookie'),
                               'x-site': 'http://bigasterisk.com/openidProxySite/href',
                           }).text

def getUser():
    agent = bottle.request.headers.get('x-foaf-agent', None)
    username = db['user'].find_one({'_id':agent})['username'] if agent else None
    return username, agent

def siteRoot():
    try:
        return bottle.request.headers['x-site-root'].rstrip('/')
    except KeyError:
        log.warn(repr(bottle.request.__dict__))
        raise
    
@bottle.route('/static/<path:path>')
def server_static(path):
    return static_file(path, root='static')

def recentLinks(user, tags, allowEdit):
    out = {'links':[]}
    t1 = time.time()
    spec = {'user':user}
    if tags:
        spec['extracted.tags'] = {'$all' : tags}
    for doc in db['links'].find(spec, sort=[('t', -1)], limit=50):
        link = links.forDisplay(doc)
        link['allowEdit'] = allowEdit
        out['links'].append(link)
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
    byFreq = [(n, t) for t,n in count.items()]
    byFreq.sort(key=lambda n_t: (-n_t[0], n_t[1]))
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
        'toRoot': siteRoot(),
        'absRoot': siteRoot(),
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
        prevDoc = links.find(uri, user)
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
    haveTags = [_f for _f in params['have'].split(',') if _f]
    if haveTags and len(haveTags[-1]) > 0:
        haveTags, partialTerm = haveTags[:-1], haveTags[-1]
    else:
        partialTerm = ""

    out = []
    for t in allTags(params.user, withTags=haveTags):
        if partialTerm and partialTerm not in t['label']:
            continue
        out.append({'id': t['label'],
         'text': "%s (%s%s)" % (t['label'],
                                t['count'],
                                " left" if haveTags else "")})
    
    return {'tags' : out}
    
@bottle.route('/<user>/')
def userSlash(user):
    bottle.redirect(siteRoot() + "/%s" % urllib.parse.quote(user))

@bottle.route('/<user>.json', method='GET')
def userAllJson(user):
    data = recentLinks(user, [], allowEdit=getUser()[0] == user)
    data['toRoot'] = siteRoot()
    return json.dumps(data)
    
@bottle.route('/<user>', method='GET')
def userAll(user):
    return userLinks(user, "")
    
   
@bottle.route('/<user>', method='POST')
def userAddLink(user):
    if getUser()[0] != user:
        raise ValueError("not logged in as %s" % user)
    print(repr(bottle.request.params.__dict__))
    doc = links.fromPostdata(bottle.request.params,
                             user,
                             datetime.datetime.now(tzlocal()))
    links.insertOrUpdate(doc)

    print("notify about sharing to", repr(doc['shareWith']))
        
    bottle.redirect(siteRoot() + '/' + user)

def parseTags(tagComponent):
    # the %20 is coming from davis.js, not me :(
    return [_f for _f in tagComponent.replace("%20", "+").split('+') if _f]
    
@bottle.route('/<user>/<tags:re:.*>.json')
def userLinksJson(user, tags):
    tags = parseTags(tags)
    data = recentLinks(user, tags, allowEdit=getUser()[0] == user)
    data['toRoot'] = siteRoot()
    return json.dumps(data)

    
@bottle.route('/<user>/<tags>')
def userLinks(user, tags):
    tags = parseTags(tags)
    log.info('userLinks user=%r tags=%r', user, tags)
    data = recentLinks(user, tags, allowEdit=getUser()[0] == user)
    data['loginBar'] = getLoginBar()
    data['desc'] = ("%s's recent links" % user) + (" tagged %s"  % (tags,) if tags else "")
    data['toRoot'] = siteRoot()
    data['allTags'] = allTags(user)
    data['user'] = user
    data['showPrivateData'] = (user == getUser()[0])

    data['pageTags'] = [{"word":t} for t in tags]
    data['stats']['template'] = 'TEMPLATETIME'
    return renderWithTime('links.jade', data)

@bottle.route('/templates')
def templates():
    return json.dumps({'linklist': renderer.load_template("linklist.jade")})
    
@bottle.route('/')
def root():
    data = {
        'loginBar': getLoginBar(),
        'toRoot': siteRoot(),
        'stats': {'template': 'TEMPLATETIME'},
        'users': [{'user':doc['username']} for doc in db['user'].find()],
        }
    return renderWithTime('index.jade', data)
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    bottle.run(server='gunicorn', host='0.0.0.0', port=10002, workers=4)
