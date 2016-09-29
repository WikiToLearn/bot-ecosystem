#!/usr/bin/env python
import wtl
import wtlpywikibot
import pywikibot
import datetime
import time
import requests
import urllib.parse

config = wtl.load_config(config_dir="/etc/pdfcheck-pages/")

DELTATIME=config['global']['deltatime']

running = True
time_debit = 0
while running:
    unix_time_start = int(time.time())
    for lang in config['pywikibot']['langs']:
        site = pywikibot.Site(lang,'wikitolearn')
        site_hostname = site.family.hostname(lang)

        if 'pywikibot' in config and 'username' in config['pywikibot'] and 'password' in config['pywikibot']:
            username=config['pywikibot']['username']
            password=config['pywikibot']['password']
            wtlpywikibot.login(site,username,password)

        recentchanges = site.recentchanges(topOnly = True, end=site.getcurrenttime()- (datetime.timedelta(seconds=DELTATIME+ time_debit)))
        for recentchange in recentchanges:
            page_title = recentchange['title']
            page = pywikibot.Page(site,page_title)
            if page.namespace() == "Template:":
                print("{} is a template...".format(page_title))
            else:
                print("Page: {}".format(page_title))
                if wtlpywikibot.get_category_status(site,page,"Structure"):
                    print("\tThis page is a 'Structure' page")
                    wtlpywikibot.set_category_status(site, page, "Broken PDF",False)
                else:
                    print("\tChecking this page...")
                    isCheckOK, message = wtlpywikibot.checkPDFforPage(site,page_title)
                    needNotification = wtlpywikibot.set_category_status(site, page, "Broken PDF",not isCheckOK)
                    if needNotification:
                        print("\tSend the notification.")
                        print("\tPDF status: {}".format(isCheckOK))
                        data = {}
                        data["title"] = page_title
                        data["page_url"] = site.family.protocol(site.code) + "://" + site.family.hostname(site.code) + "/" + urllib.parse.quote(page_title)
                        if isCheckOK:
                            wtl.send_notify(data,"fixed",config['gateway'])
                        else:
                            wtl.send_notify(data,"error",config['gateway'])
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
