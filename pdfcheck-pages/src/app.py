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
        site = wtlpywikibot.site(lang)
        site_hostname = site.family.hostname(lang)

        recentchanges = site.recentchanges(topOnly = True, end=site.getcurrenttime()- (datetime.timedelta(seconds=DELTATIME+ time_debit)))
        for recentchange in recentchanges:
            page_title = recentchange['title']
            page = pywikibot.Page(site,page_title)
            check = False
            if page.namespace() == "Course:":
                print("Is in the Course namespace...")
                if len(page.title().split('/')) == 3:
                    print("Is a page in the 3th level =>  check")
                    check = True
            elif page.namespace() == "User:":
                print("Is in the User namespace...")
                if len(page.title().split('/')) == 4:
                    print("Is a page in the 4th level => check")
                    check = True
            if check:
                print("\tChecking this page...")
                broken_math = []
                for math in wtlpywikibot.extract_math(page.text):
                    print("Math:")
                    print(math)
                    try:
                        print("Status: {}".format(wtlpywikibot.check_formula(site,math)))
                    except Exception as e:
                        broken_math.append(math)
                        print(e)
                    print()
                isCheckOK, message = wtlpywikibot.checkPDFforPage(site,page_title)
                print("\tPDF status: {}".format(isCheckOK))
                data = {}
                data["title"] = page_title
                data["page_url"] = site.family.protocol(site.code) + "://" + site.family.hostname(site.code) + "/" + urllib.parse.quote(page_title)
                data["broken_math"] = broken_math
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
