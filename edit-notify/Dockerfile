FROM wikitolearn/pywikibot:0.3.3

ADD ./src/ /opt/
WORKDIR /opt/

ENV PYTHONUNBUFFERED=0

ENTRYPOINT /opt/app.py
