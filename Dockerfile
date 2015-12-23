FROM wikitolearn/pywikibot:0.1

MAINTAINER wikitolearn sysadmin@wikitolearn.org
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

WORKDIR /pywikibot/

ADD ./* pdfcheck/
RUN mv pdfcheck/* ./

RUN mv wikitolearn_family.py /pywikibot/pywikibot/families/
RUN pip install -r pdfcheck_requirements.txt

RUN chmod +x run.sh

CMD ["./run.sh"]

