FROM wikitolearn/pywikibot:0.1.1

MAINTAINER wikitolearn sysadmin@wikitolearn.org
ENV DEBIAN_FRONTEND noninteractive
ENV DEBCONF_NONINTERACTIVE_SEEN true

ADD ./pdfcheck_requirements.txt /w2lbot/
ADD ./check.py /w2lbot/
ADD ./run.py /w2lbot/

WORKDIR /w2lbot/
RUN pip install --target=/w2lbot/ -r pdfcheck_requirements.txt

CMD ["python","run.py"]

