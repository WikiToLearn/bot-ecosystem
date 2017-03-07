#!/usr/bin/env python
import wtl
import wtlpywikibot
import pywikibot
import datetime
import time
import requests
import urllib.parse

config = wtl.load_config(config_dir="/etc/pdfcheck-collections/")

DELTATIME=config['global']['deltatime']

running = True
time_debit = 0
while running:
    unix_time_start = int(time.time())
    for lang in config['pywikibot']['langs']:
        site = wtlpywikibot.site(lang)
        site_hostname = site.family.hostname(lang)
        report = {}
        report['lang'] = lang
        report['lists'] = {}
        report['lists'][True] = []
        report['lists'][False] = []

        for collection_page in site.allpages(namespace=4):
            if len(collection_page.title().split('/')) > 1:
                print(collection_page.title())
                isCheckOK, message = wtlpywikibot.checkPDFforPage(site,collection_page.title(),isCollection=True)
                data = {}
                data["title"] = collection_page.title()
                data["collection_url"] = site.family.protocol(site.code) + "://" + site.family.hostname(site.code) + "/" + urllib.parse.quote(collection_page.title())
                if isCheckOK:
                    wtl.send_notify(data,"success",config['gateway'])
                else:
                    data["broken_pages"] = []
                    for line in collection_page.text.split('\n'):
                        try:
                            if line[0:3]==":[[":
                                page_title = line[3:-2]
                                page = pywikibot.Page(site,page_title)
                                broken_math = []
                                for math in wtlpywikibot.extract_math(page.text):
                                    try:
                                        print("Status: {}".format(wtlpywikibot.check_formula(site,math)))
                                    except Exception as e:
                                        broken_math.append(math)
                                dataPage = {}
                                dataPage["title"] = page_title
                                dataPage["page_url"] = site.family.protocol(site.code) + "://" + site.family.hostname(site.code) + "/" + urllib.parse.quote(page_title)
                                dataPage["broken_math"] = broken_math

                                isCheckPageOK, messagePage = wtlpywikibot.checkPDFforPage(site,page_title)
                                if not isCheckPageOK:
                                    print(" Page {} is KO".format(page_title))
                                    data["broken_pages"].append(dataPage)
                        except Exception as e:
                            print(e)
                    wtl.send_notify(data,"error",config['gateway'])
                report['lists'][isCheckOK].append(data)

        if len(report['lists'][False]) > 0:
            wtl.send_notify(report,"report",config['gateway'])

    unix_time_end = int(time.time())
    waiting_time=DELTATIME - (unix_time_end-unix_time_start)
    if waiting_time > 0:
        print("Wait for: {} s".format(waiting_time))
        for s in range(0, DELTATIME - (unix_time_end - unix_time_end)):
            time.sleep(1)
        time_debit = 0
    else:
        time_debit = -1 * waiting_time
