FROM wikitolearn/python35:0.1
RUN pip install flask
RUN pip install python-telegram-bot

ADD ./src/ /opt/
WORKDIR /opt/

EXPOSE 5000

ENV PYTHONUNBUFFERED=0

ENTRYPOINT /opt/app.py
