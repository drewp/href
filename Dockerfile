FROM bang5:5000/base_x86

WORKDIR /opt

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata

COPY requirements.txt ./

RUN pip3 install 'BeautifulSoup4'
RUN pip3 install 'CherryPy==3.2.2'
RUN pip3 install 'argparse==1.2.1'
RUN pip3 install 'bottle==0.11.6'
RUN pip3 install 'cssselect==0.7.1'
RUN pip3 install 'gunicorn==0.17.2'
RUN pip3 install 'http-parser==0.8.1'
RUN pip3 install 'pymongo==2.4.2'
RUN pip3 install 'pystache==0.5.3'
RUN pip3 install 'python-dateutil'
RUN pip3 install 'six'
RUN pip3 install 'pyjade==4.0.0'
RUN pip3 install 'lxml==4.5.2'
RUN pip3 install 'requests==2.24.0'


RUN pip3 install --index-url https://projects.bigasterisk.com/ --extra-index-url https://pypi.org/simple -r requirements.txt
RUN pip3 install -U 'https://github.com/drewp/cyclone/archive/python3.zip?v3'

COPY *.py run ./
COPY static static/
COPY template template/


CMD [ "./run" ]
