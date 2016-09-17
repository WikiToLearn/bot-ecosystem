FROM wikitolearn/pywikibot:0.2.2
RUN pip install pyyaml
RUN pip install requests

ADD ./src/ /opt/
WORKDIR /opt/

ENV PYTHONUNBUFFERED=0

ENTRYPOINT /opt/app.py
