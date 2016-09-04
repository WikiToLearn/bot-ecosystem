#!/usr/bin/env python
import yaml
import os, sys
import wtlpywikibot
import pywikibot
from pywikibot import pagegenerators
from pywikibot import textlib
import datetime
import urllib.parse
import time
import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
import argparse
from pywikibot.data import api
from pywikibot.site import LoginStatus

def category_status(site, page, cat, status):
    old_text = page.text
    cats = textlib.getCategoryLinks(old_text)
    catpl = pywikibot.Category(site, cat)

    if status:
        if catpl not in cats:
            print("\t'" + cat + "' not in page categories. Adding")
            cats.append(catpl)
    else:
        if catpl in cats:
            print("\t'" + cat + "' in page categories. Adding")
            cats.remove(catpl)
    text = textlib.replaceCategoryLinks(page.text, cats, site=site)
    if old_text != text:
        page.text = text
        page.save(minor=True, botflag=True)
        return True
    return False

def checkPDFforPage(page_url, site_hostname):
    result_bool = None
    result_text = None
    try:
        headers = {
            'User-Agent': 'PDF Check - WikiToLearn'
        }
        r = requests.get(page_url, headers=headers)

        print("\tPage Downloaded")

        dom = BeautifulSoup(r.text, 'html.parser')

        li_pdf = dom.find(id="coll-download-as-rdf2latex")
        if li_pdf:
            a_pdf = li_pdf.find('a').get('href')
            r_pdf = requests.head("http://" + site_hostname + a_pdf, headers=headers, allow_redirects=True)
            print("\tDo PDF request sent")

            par = urlparse.parse_qs(urlparse.urlparse(r_pdf.url).query)
            collection_id = par['collection_id'][0]

            url_check = "http://" + site_hostname + "/index.php?action=ajax&rs=wfAjaxGetMWServeStatus&rsargs%5B%5D=" + collection_id + "&rsargs%5B%5D=rdf2latex";

            checks = 0
            print("\tChecking PDF Generation Status")

            running = True
            while running:
                print("\tRequesting Status " + str(checks) + "...")
                r_checkStatus = requests.get(url_check, headers=headers)
                checks+=1

                status = r_checkStatus.json()[u"status"]

                if(status["progress"] == "100.00"):
                    result_bool = True
                    result_text = "PDF OK"
                    running = False
                    print("FINISH")
                elif("error" in status["status"].lower()) or ("died" in status["status"].lower()):
                    result_bool = False
                    result_text = status['status']
                    running = False
                    print("FAIL")
                    print(status)

                time.sleep(1)
        else:
            result_bool = True
            result_text = "No PDF can be downloaded for this page"

    except requests.exceptions.RequestException as e:
        result_bool = False
        result_text = str(e)
    return result_bool,result_text

def send(data,notify_type):
    protocol = config['gateway']['protocol']
    hostname = config['gateway']['hostname']
    port = config['gateway']['port']
    token = config['gateway']['token']
    url = '{}://{}:{}/api/sendNotify'.format(protocol,hostname,port)
    data_to_send = {"service": config['gateway']['service'],"type":notify_type,"token":token,"payload":data}
    r = requests.post(url, json=data_to_send)

stream = open('config.yaml', 'r')
config = yaml.load(stream, Loader=yaml.Loader)

DELTATIME=config['global']['deltatime']

running = True
time_debit = 0
while running:
    unix_time_start = int(time.time())
    for lang in config['pywikibot']['langs']:
        site = pywikibot.Site(lang,'wikitolearn')
        site_hostname = site.family.hostname(lang)

        if 'pywikibot' in config:
            if 'username' in config['pywikibot'] and 'password' in config['pywikibot']:
                username=config['pywikibot']['username']
                password=config['pywikibot']['password']
                wtlpywikibot.login(lang,'wikitolearn',username,password)

        recentchanges = site.recentchanges(topOnly = True, end=site.getcurrenttime()- (datetime.timedelta(seconds=(DELTATIME+ time_debit))))
        for recentchange in recentchanges:
            page_title = recentchange['title']
            page = pywikibot.Page(site,page_title)
            page_url = page.full_url()
            print("Page: {}".format(page_title))
            if pywikibot.Category(site,"Structure") in pywikibot.Page(site, page_title).categories():
                print("\tPage " + page_url + " IN 'Structure' category")
                category_status(site, pywikibot.Page(site, page_title), "Broken PDF",False)

            else:
                isCheckOK, message = checkPDFforPage(page_url, site_hostname)
                needNotification = category_status(site, pywikibot.Page(site, page_title), "Broken PDF",not isCheckOK)
                if needNotification:
                    data = {}
                    data["title"] = page_title
                    data["page_url"] = page_url
                    if isCheckOK:
                        send(data,"fixed")
                    else:
                        send(data,"error")
            print(recentchange)
        print("\n")
    unix_time_end = int(time.time())
    waiting_time=DELTATIME - (unix_time_end-unix_time_start)
    if waiting_time > 0:
        print("Wait for: {} s".format(waiting_time))
        for s in range(0, DELTATIME - (unix_time_end - unix_time_end)):
            time.sleep(1)
        time_debit = 0
    else:
        time_debit = -1 * waiting_time
