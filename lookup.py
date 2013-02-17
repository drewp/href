#!bin/python
"""
serve some queries over bookmarks:

/user
/user/tag+tag+tag

"""
import pymongo, bottle, time, urllib
from urllib2 import urlparse
from dateutil.tz import tzlocal
from bottle import static_file
from jadestache import Renderer
db = pymongo.Connection('bang', tz_aware=True)['href']

renderer = Renderer(search_dirs=['template'], debug=bottle.DEBUG)

@bottle.route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')

def recentTags(user, tags=None):
    out = {'links':[]}
    t1 = time.time()
    spec = {'user':user}
    if tags:
        spec['extracted.tags'] = {'$all' : tags}
    for doc in db['links'].find(spec, sort=[('t', -1)], limit=50):
        del doc['_id']
        doc['t'] = doc['t'].astimezone(tzlocal()).isoformat()
        if not doc['description'].strip():
            doc['displayDescription'] = doc['href']
        else:
            doc['displayDescription'] = doc['description']

        doc['tagWords'] = [{'word' : w} for w in doc['tag'].split(None)]
        doc['domain'] = urlparse.urlparse(doc['href']).netloc
        
        out['links'].append(doc)
    out['stats'] = {'queryTimeMs' : round((time.time() - t1) * 1000, 2)}
    return out

def renderWithTime(name, data):
    t1 = time.time()
    rendered = renderer.render_name("links.jade", data)
    dt = (time.time() - t1) * 1000
    rendered = rendered.replace('TEMPLATETIME', "%.02f ms" % dt)
    return rendered
    
@bottle.route('/<user>/')
def userSlash(user):
    bottle.redirect("/%s" % urllib.quote(user))
    
@bottle.route('/<user>')
def userAll(user):
    data = recentTags(user, tags=None)

    data['desc'] = "%s's recent links" % user
    data['toRoot'] = "."
    data['stats']['template'] = 'TEMPLATETIME'
    return renderWithTime('links.jade', data)
    
@bottle.route('/<user>/<tags>')
def userLinks(user, tags):
    tags = tags.split('+')
    data = recentTags(user, tags)
    data['desc'] = "%s's recent links tagged %s"  % (user, tags)
    data['toRoot'] = ".."

    data['pageTags'] = [{"word":t} for t in tags]
    data['stats']['template'] = 'TEMPLATETIME'
    return renderWithTime('links.jade', data)
    
if __name__ == '__main__':
    bottle.run(server='gunicorn', host='0.0.0.0', port=10002, workers=4)