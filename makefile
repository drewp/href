all: bin/python static/lib/jquery-1.9.1.min.js static/lib/knockout-2.2.1.js static/lib/select2 static/lib/async-2013-03-17.js static/lib/jquery.rdfquery.rdfa.min-1.0.js static/lib/RDFa.min.0.21.0.js

bin/python:
	bin/pip install -r pydeps

static/lib/jquery-1.9.1.min.js:
	curl -o $@ http://code.jquery.com/jquery-1.9.1.min.js

static/lib/knockout-2.2.1.js:
	curl -o $@ http://knockoutjs.com/downloads/knockout-2.2.1.js

static/lib/select2:
	git clone git://github.com/ivaynberg/select2.git static/lib/select2
	(cd static/lib/select2; git checkout --quiet 4530e74e95)

static/lib/async-2013-03-17.js:
	curl -o $@ https://raw.github.com/caolan/async/522d97f3d1d8a708265827ae23a66ccf30c5821c/lib/async.js

static/lib/jquery.rdfquery.rdfa.min-1.0.js:
	curl -o $@ https://rdfquery.googlecode.com/files/jquery.rdfquery.rdfa.min-1.0.js

static/lib/RDFa.min.0.21.0.js:
	curl -o $@ https://green-turtle.googlecode.com/files/RDFa.min.0.21.0.js
