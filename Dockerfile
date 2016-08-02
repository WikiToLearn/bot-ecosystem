FROM wikitolearn/pywikibot:0.1.3
RUN pip install pyyaml
RUN pip install requests
RUN pip install beautifulsoup4==4.4.1
RUN pip install httplib2==0.9.2
RUN pip install ipaddress==1.0.15
RUN pip install wheel==0.24.0

ADD ./src/ /w2lbot/
WORKDIR /w2lbot/

CMD /w2lbot/app.py
