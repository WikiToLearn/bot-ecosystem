#!/usr/bin/env python3
import wtl
from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)

@app.route("/ref/<action>", methods=['POST'])
def flask_post_git_ref_action(action):
    ref_name = None
    ref_type = None
    reponame = None
    if 'ref_name' in request.form:
        ref_name = request.form['ref_name']
    if 'ref_type' in request.form:
        ref_type = request.form['ref_type']
    if 'reponame' in request.form:
        reponame = request.form['reponame']
    if action == "added" or action == "deleted":
        wtl.send_notify({"ref_name": ref_name, "ref_type": ref_type,"reponame": reponame}, "ref_{}".format(action),config['gateway'])
    return "OK\n"


@app.route("/commit", methods=['POST'])
def flask_post_git_commit():
    reponame = None
    commit_message = None
    commit = None
    committer_email = None
    committer_name = None
    ref_name = None
    ref_type = None
    if 'commit_message' in request.form:
        commit_message = request.form['commit_message']
    if 'commit' in request.form:
        commit = request.form['commit']
    if 'committer_email' in request.form:
        committer_email = request.form['committer_email']
    if 'committer_name' in request.form:
        committer_name = request.form['committer_name']
    if 'ref_name' in request.form:
        ref_name = request.form['ref_name']
    if 'ref_type' in request.form:
        ref_type = request.form['ref_type']
    if 'reponame' in request.form:
        reponame = request.form['reponame']
    wtl.send_notify({"commit_message":commit_message,"commit":commit,"committer_name":committer_name,"committer_email":committer_email,"ref_name":ref_name,"ref_type":ref_type,"reponame":reponame}, "commit",config['gateway'])
    return "OK\n"


@app.route('/')
def hello_world():
    return 'Hello, this is the Git adapter!'


config = wtl.load_config(config_dir="/etc/git-adapter/")

app.run(host='0.0.0.0', port=5003)
