#!/usr/bin/env python3
import wtl
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route('/proxyCommand', methods=['POST'])
def proxyCommand():
    hostname = None
    if 'hostname' in request.form:
        hostname = request.form['hostname']
    loginfrom = None
    if 'loginfrom' in request.form:
        loginfrom = request.form['loginfrom']
    username = None
    if 'username' in request.form:
        username = request.form['username']
    username = None
    if 'username' in request.form:
        username = request.form['username']
    to_host = None
    if 'to_host' in request.form:
        to_host = request.form['to_host']
    to_port = None
    if 'to_port' in request.form:
        to_port = request.form['to_port']
    wtl.send_notify({
        'hostname':hostname,
        'loginfrom':loginfrom,
        'username':username,
        'to_host':to_host,
        'to_port':to_port,
    },"login-proxy",config['gateway'])
    return "OK"

@app.route('/loginNotify', methods=['POST'])
def loginNotify():
    hostname = None
    if 'hostname' in request.form:
        hostname = request.form['hostname']
    loginfrom = None
    if 'loginfrom' in request.form:
        loginfrom = request.form['loginfrom']
    username = None
    if 'username' in request.form:
        username = request.form['username']
    wtl.send_notify({
        'hostname':hostname,
        'loginfrom':loginfrom,
        'username':username
    },"login",config['gateway'])
    return "OK"

@app.route('/')
def hello_world():
    return 'Hello, this is the Server Status adapter!'


config = wtl.load_config(config_dir="/etc/server-status-adapter/")

app.run(host='0.0.0.0',port=5002)
