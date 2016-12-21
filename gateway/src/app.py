#!/usr/bin/env python3
import wtl
import telegram
import time

from jinja2 import Template
from flask import Flask
from flask import jsonify
from flask import request

from pprint import pprint
import re

import sys

#def costum_excepthook(exctype, value, traceback):
#    print("Exception: ")
#    print("\t{}".format(exctype))
#    print("\t{}".format(value))
#    print("\t{}".format(traceback))
#sys.excepthook = costum_excepthook

app = Flask(__name__)

def resp_json(data):
    callback = request.values.get('callback', False)
    if callback:
        content = str(callback) + '(' + str(jsonify(data).data) + ')'
        resp = current_app.response_class(content, mimetype='application/json')
    else:
        resp = jsonify(data)
    return resp

def channels_conditional_check(conditions,payload):
    status = False
    for condition in conditions:
        condition_status = len(condition) > 0 and len(payload) > 0
        for rule in condition:
            if rule['check_type'] == 'regex':
                if rule['var'] in payload:
                    regex = re.compile(rule['regex'])
                    regex_match = (regex.match(payload[rule['var']]) != None)
                    condition_status = condition_status and regex_match
                else:
                    condition_status = False
            else:
                condition_status = False
        status = status or condition_status
    return status

def find_channels(destination,payload):
    channels = []
    if 'channels' in destination:
        for c in destination['channels']:
            channels.append(c)
    if 'channel' in destination:
        channels.append(destination['channel'])
    if 'channels_conditional' in destination:
        for channel_conditional in destination['channels_conditional']:
            if channel_conditional['channel'] not in channels:
                if channels_conditional_check(channel_conditional['conditions'],payload):
                    channels.append(channel_conditional['channel'])
    return channels

def send_to_destinations(destinations,reply,payload):
    for destination in destinations:
        if config['outgoing'][destination['outgoing_id']]['type'] == "telegram":
            channels = find_channels(destination,payload)
            for channel in channels:
                template = Template(destination['message'])
                telegram_msg = template.render(**payload)
                reply["sent"].append(destination)
                telegram_bots[destination['outgoing_id']].sendMessage(
                    channel, telegram_msg,disable_web_page_preview=True)
        elif config['outgoing'][destination['outgoing_id']]['type'] == "rocketchat":
            channels = find_channels(destination,payload)
            for channel in channels:
                template = Template(destination['message'])
                rocketchat_msg = template.render(**payload)
                reply["sent"].append(destination)
                rocketchat_bots[destination['outgoing_id']].chat_postMessage(
                    channel, rocketchat_msg)
    if len(reply["sent"]) == 0:
        print("Not sent:")
        pprint(request.json)

@app.route('/api/sendNotify', methods=['POST'])
def api_sendNotify_POST():
    reply = {}
    reply['errors'] = []
    if request.headers['Content-Type'] != 'application/json':
        reply['errors'].append("ERR_CONTENT_TYPE")
    else:
        print("Request data: {}".format(request.json))
        if 'service' not in request.json:
            reply['errors'].append("NO_SERVICE_SET")

        if 'type' not in request.json:
            reply['errors'].append("NO_TYPE_SET")

        if 'token' not in request.json:
            reply['errors'].append("NO_TOKEN_SET")

        if 'payload' not in request.json:
            reply['errors'].append("NO_PAYLOAD_SET")

        if len(reply['errors']) == 0:
            services = config['services']
            if request.json['service'] in services:
                service_name = request.json['service']
                service_types = services[service_name]['types']
                if request.json['type'] in service_types:
                    notify_type = request.json['type']
                    token = request.json['token']
                    acls = []
                    if 'allow' in service_types[notify_type]:
                        acls = acls + service_types[notify_type]['allow']
                    if 'allow' in services[service_name]:
                        acls = acls + services[service_name]['allow']
                    destinations = []
                    if 'destinations' in service_types[notify_type]:
                        destinations = destinations + \
                            service_types[notify_type]['destinations']
                    payload = request.json['payload']
                    allowSend = False
                    for acl in acls:
                        if acl == '*':
                            allowSend = True
                        elif acl == token:
                            allowSend = True
                    if allowSend:
                        reply["sent"] = []
                        send_to_destinations(destinations,reply,payload)
                    else:
                        reply["errors"].append("NOT_ALLOWED")
                else:
                    reply["errors"].append("TYPE_NOT_FOUND")
            else:
                reply["errors"].append("SERVICE_NOT_FOUND")
    if len(reply["errors"]) > 0:
        print(request.json)
        print(reply)
        print()
    return resp_json(reply)

@app.route('/')
def hello_world():
    return 'Hello, this is the main WikiToLearn Bot gateway!'

config = wtl.load_config(config_dir="/etc/gateway/")

telegram_bots = {}
rocketchat_bots = {}

for outgoing_id in config['outgoing']:
    if config['outgoing'][outgoing_id]['type'] == "telegram":
        if config['outgoing'][outgoing_id]['token'] == "test":
            from fakeoutput import FakeTelegramBot
            telegram_bots[outgoing_id] = FakeTelegramBot.FakeTelegramBot()
        else:
            telegram_bots[outgoing_id] = telegram.Bot(
                config['outgoing'][outgoing_id]['token'])
    elif config['outgoing'][outgoing_id]['type'] == "rocketchat":
        from RocketChat import RocketChat
        rocketchat_bots[outgoing_id] = RocketChat(
            config['outgoing'][outgoing_id]['baseurl'],
            config['outgoing'][outgoing_id]['username'],
            config['outgoing'][outgoing_id]['password']
        )

print("Starting gateway...")
app.run(host='0.0.0.0')
