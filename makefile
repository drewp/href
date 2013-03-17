all: bin/python static/lib/jquery-1.9.1.min.js static/lib/knockout-2.2.1.js static/lib/select2

bin/python:
	bin/pip install -r pydeps

static/lib/jquery-1.9.1.min.js:
	curl -o $@ http://code.jquery.com/jquery-1.9.1.min.js

static/lib/knockout-2.2.1.js:
	curl -o $@ http://knockoutjs.com/downloads/knockout-2.2.1.js

static/lib/select2:
	git clone git://github.com/ivaynberg/select2.git static/lib/select2
	(cd static/lib/select2; git checkout --quiet 4530e74e95)
