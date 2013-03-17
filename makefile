all: bin/python static/lib/jquery-1.9.1.min.js static/lib/knockout-2.2.1.js static/lib/select2-3.3.1

bin/python:
	bin/pip install -r pydeps

static/lib/jquery-1.9.1.min.js:
	curl -o $@ http://code.jquery.com/jquery-1.9.1.min.js

static/lib/knockout-2.2.1.js:
	curl -o $@ http://knockoutjs.com/downloads/knockout-2.2.1.js

static/lib/select2-3.3.1:
	curl -L -o /tmp/select2.zip https://github.com/ivaynberg/select2/archive/3.3.1.zip 
	(cd static/lib; unzip /tmp/select2.zip)
