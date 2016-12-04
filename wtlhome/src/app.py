#!/usr/bin/env python3
import wtl
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route("/event/<domain>", methods=['POST'])
def flask_post_wtlhome(domain):
    data = {"domain": domain}
    for key in request.form:
        data[key] = request.form[key]
    wtl.send_notify(data, "event",config['gateway'])

    return "OK\n"

@app.route('/release/found', methods=['POST'])
def release_found():
    commit = None
    if 'commit' in request.form:
        commit = request.form['commit']
    host = None
    if 'host' in request.form:
        host = request.form['host']
    baseurl = None
    if 'baseurl' in request.form:
        baseurl = request.form['baseurl']
    wtl.send_notify({
        'commit':commit,
        'host':host,
        'baseurl':baseurl
    },"release_found",config['gateway'])
    return "OK"


@app.route('/release/online', methods=['POST'])
def release_online():
    commit = None
    if 'commit' in request.form:
        commit = request.form['commit']
    host = None
    if 'host' in request.form:
        host = request.form['host']
    baseurl = None
    if 'baseurl' in request.form:
        baseurl = request.form['baseurl']
    wtl.send_notify({
        'commit':commit,
        'host':host,
        'baseurl':baseurl
    },"release_online",config['gateway'])
    return "OK"

@app.route('/')
def hello_world():
    return 'Hello, this is the WikiToLearn Home adapter!'


config = wtl.load_config(config_dir="/etc/wtlhome/")

app.run(host='0.0.0.0', port=5004)
