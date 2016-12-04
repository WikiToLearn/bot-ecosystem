#!/usr/bin/env python3
import wtl
from flask import Flask
from flask import jsonify
from flask import request
import random
import requests
import hmac
from hashlib import sha1
from sys import hexversion

app = Flask(__name__)

def allow_github_secret():
    allow = True
    if 'github' in config and 'secret' in config['github']:
        header_signature = request.headers.get('X-Hub-Signature')
        if header_signature is None:
            allow = False
        sha_name, signature = header_signature.split('=')
        if sha_name != 'sha1':
            allow = False
        mac = hmac.new(bytearray(config['github']['secret'], "ASCII"), msg=request.data, digestmod=sha1)
        if hexversion >= 0x020707F0:
            if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
                allow = False
        else:
            if not str(mac.hexdigest()) == str(signature):
                allow = False
    return allow

@app.route('/github/push', methods=['POST'])
def github_push_post():
    if allow_github_secret() and 'repository' in request.json:
        repo_name = request.json['repository']['name']
        branch = request.json['ref'].split('/')[2]
        for commit in request.json['commits']:
            ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
            chars=[]
            for i in range(16):
                chars.append(random.choice(ALPHABET))
            code = "".join(chars)

            data_to_send = {"code":code,"url":commit['url']}
            r = requests.post("https://git.io/create", data=data_to_send)

            wtl.send_notify({
            "repo":repo_name,
            "branch":branch,
            "commit_id":commit['id'],
            "commit_author_name":commit['author']['name'],
            "commit_message":commit['message'],
            "commit_url":commit['url'],
            "commit_url_short":"https://git.io/{}".format(r.text)
            },"commit",config['gateway'])
    return "OK"

@app.route('/github/create', methods=['POST'])
def github_create_post():
    if allow_github_secret() and 'repository' in request.json:
        repo_name = request.json['repository']['name']
        ref_type = request.json['ref_type']
        ref = request.json['ref']
        wtl.send_notify({
        "repo":repo_name,
        "ref_type":ref_type,
        "ref":ref
        },"create",config['gateway'])
    return "OK"

@app.route('/')
def hello_world():
    return 'Hello, this is the GitHub adapter!'

config = wtl.load_config(config_dir="/etc/github-adapter/")

app.run(host=config['app']['bind_addr'],port=5001)
