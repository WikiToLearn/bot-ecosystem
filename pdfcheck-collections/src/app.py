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

        for page in site.allpages(namespace=4):
            if len(page.title().split('/')) > 1:
                print(page.title())
                isCheckOK, message = wtlpywikibot.checkPDFforPage(site,page.title(),isCollection=True)
                data = {}
                data["title"] = page.title()
                data["collection_url"] = site.family.protocol(site.code) + "://" + site.family.hostname(site.code) + "/" + urllib.parse.quote(page.title())
                if isCheckOK:
                    wtl.send_notify(data,"success",config['gateway'])
                else:
                    wtl.send_notify(data,"error",config['gateway'])
    unix_time_end = int(time.time())
    waiting_time=DELTATIME - (unix_time_end-unix_time_start)
    if waiting_time > 0:
        print("Wait for: {} s".format(waiting_time))
        for s in range(0, DELTATIME - (unix_time_end - unix_time_end)):
            time.sleep(1)
        time_debit = 0
    else:
        time_debit = -1 * waiting_time
