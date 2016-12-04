#!/usr/bin/env python3
import wtl
import json
import requests
import sys
import os
import time
import datetime

config = wtl.load_config(config_dir="/etc/phabricator/")

api_token = config['phabricator']['token']
projects_names = config['phabricator']['projects']

def makePhabricatorGet(uri,data):
    data['api.token'] = api_token
    url = 'https://phabricator.kde.org/api/{}'.format(uri)
    response = requests.get(url, data=data)
    response_obj = json.loads(response.content.decode('UTF-8'))
    if response_obj['error_info'] != None:
        raise  Exception(response_obj['error_info'], response_obj['error_code'])
    return response_obj["result"]

phab_projects_id = []
for phab_project_id in makePhabricatorGet('project.query', {'names[]': projects_names})['data']:
    phab_projects_id.append(phab_project_id)

chronologicalKey = None
startup_time = int(time.time())

run = True
while run:  # get feed query
    print("REQUEST")
    feed_query_params = {}
    feed_query_params['limit'] = 1 # get 100 items each time
    #feed_query_params['view'] = 'text'
    feed_query_params['filterPHIDs[]'] = phab_projects_id
    if chronologicalKey != None:
        feed_query_params['before'] = chronologicalKey
    object_feed_query = makePhabricatorGet("feed.query", feed_query_params)

    for object_feed_query_key in object_feed_query:
        if chronologicalKey != None:
            authorPHID = object_feed_query[object_feed_query_key]['authorPHID']
            authors = makePhabricatorGet('phid.query', {'phids[]':authorPHID})

            objectPHID = object_feed_query[object_feed_query_key]['data']['objectPHID']
            objects = makePhabricatorGet('phid.query', {'phids[]':objectPHID})

            data = {}
            for d in authors:
                data['author'] = authors[d]
            for d in objects:
                data['object'] = objects[d]
            print(authors)
            print()
            print(objects)
            print()

            print(data)
            print()

            if data['object']['type'] == "TASK":
                wtl.send_notify({
                "author_name":data['author']['name'],
                "author_fullName":data['author']['fullName'],
                "author_uri":data['author']['uri'],
                "task_name":data['object']['name'],
                "task_fullName":data['object']['fullName'],
                "task_uri":data['object']['uri'],
                "task_status":data['object']['status'],
                },"task",config['gateway'])
        chronologicalKey = object_feed_query[object_feed_query_key]['chronologicalKey']
    time.sleep(int(config['phabricator']['polling_time']))
