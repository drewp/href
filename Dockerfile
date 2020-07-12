FROM bang5:5000/base_x86

WORKDIR /opt

RUN DEBIAN_FRONTEND=noninteractive apt-get install -y tzdata

COPY requirements.txt ./

RUN pip3 install --index-url https://projects.bigasterisk.com/ --extra-index-url https://pypi.org/simple -r requirements.txt

COPY *.py run ./
COPY static static/
COPY template template/


CMD [ "./run" ]
