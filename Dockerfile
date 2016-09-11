FROM wikitolearn/pywikibot:0.2
RUN pip install pyyaml
RUN pip install requests
RUN pip install beautifulsoup4==4.4.1
RUN pip install httplib2==0.9.2
RUN pip install ipaddress==1.0.15
RUN pip install wheel==0.24.0

ADD ./src/ /opt/
WORKDIR /opt/

ENV PYTHONUNBUFFERED=0

ENTRYPOINT /opt/app.py
