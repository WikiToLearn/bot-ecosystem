FROM wikitolearn/pywikibot:0.2.6

ADD ./src/ /opt/
WORKDIR /opt/

ENV PYTHONUNBUFFERED=0

ENTRYPOINT /opt/app.py
