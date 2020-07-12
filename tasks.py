from invoke import task, Collection

import sys
sys.path.append('/my/proj/release')
from serv_tasks import serv_tasks, dockerCommand
ns = Collection()
serv_tasks(ns, 'serv.n3', 'href')
