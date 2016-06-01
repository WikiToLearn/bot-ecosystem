# -*- coding: utf-8 -*-
import pywikibot
from pywikibot import textlib

import requests
import urllib.parse as urlparse
from bs4 import BeautifulSoup

import time
import datetime
import sys
import os
import argparse

config = __import__("user-config")

##Telegram Stuff
TG_API_KEY = os.environ.get('TG_API_KEY')
TG_CHAT_ID = os.environ.get('TG_CHAT_ID')

def userPut(page, oldtext, newtext, **kwargs):
    if oldtext == newtext:
        return

    current_page = page

    page.text = newtext
    return page.save(**kwargs)

def addCategory(site, page, cat):
    old_text = page.text
    cats = textlib.getCategoryLinks(old_text)

    catpl = pywikibot.Category(site, cat)

    if catpl not in cats:
        print("\t'" + cat + "' not in page categories. Adding") 
        cats.append(catpl)
        text = textlib.replaceCategoryLinks(page.text, cats, site=site)
        userPut(page, old_text, text, minor=True, botflag=True)
        return True
    else:
        print("\t'" + cat + "' already in page categories")
        return False

def checkPDFforPage(page_url, BASE_SITE):
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
            r_pdf = requests.head("http://" + BASE_SITE + a_pdf, headers=headers, allow_redirects=True)
            print("\tDo PDF request sent")
            
            par = urlparse.parse_qs(urlparse.urlparse(r_pdf.url).query)
            collection_id = par['collection_id'][0]

            url_check = "http://" + BASE_SITE + "/index.php?action=ajax&rs=wfAjaxGetMWServeStatus&rsargs%5B%5D=" + collection_id + "&rsargs%5B%5D=rdf2latex";
            
            checks = 0
            print("\tChecking PDF Generation Status")

            while True:
                print("\tRequesting Status " + str(checks) + "...")
                r_checkStatus = requests.get(url_check, headers=headers)
                checks+=1

                status = r_checkStatus.json()[u"status"]

                if(status["progress"] == "100.00"):
                    return True, "Converted to PDF"

                if("error" in status["status"].lower()):
                    return False, status["status"]

                time.sleep(1)
        else:
            return True, "No PDF can be downloaded for this page"

    except requests.exceptions.RequestException as e:
        print(e)
        sys.exit(1)

def sendTelegramNotification(message):
    if (TG_API_KEY is not None) and (TG_CHAT_ID is not None):
        payload = { 'chat_id': TG_CHAT_ID, 
        'text': message,
        'parse_mode': 'Markdown' }
        requests.get("https://api.telegram.org/bot" + TG_API_KEY + "/sendmessage", params=payload)
    else:
        print("Telegram ENV variables are not set!")


def generateBookPages(BOOK_URL):
    headers = {
        'User-Agent': 'PDF Check - WikiToLearn'
    }
    r = requests.get(BOOK_URL, headers=headers)

    dom = BeautifulSoup(r.text, 'html.parser')
    mwContent = dom.find(id="mw-content-text")
    dd = mwContent.findAll('dd')
    pages = []
    for link in dd:
        page = {}
        page["title"] = link.get_text()
        pages.append(page)

    return pages

def main(MODE, DELTATIME, BOOK_URL, PAGE_NAME):   
    print("Connecting to " + config.mylang + " domain for the " + config.family + " family")
    site = pywikibot.Site()
    
    BASE_SITE = site.family.langs[config.mylang]
    print("Base URL: " + BASE_SITE)
    
    if MODE == "r":
        print("Checking most recent edits")
        pages = site.recentchanges(topOnly = True, end=site.getcurrenttime()- datetime.timedelta(minutes=DELTATIME))
    elif MODE == "a":
        print("Checking all pages")
        pages = site.allpages()
    elif MODE == "b":
        print("Checking book")
        pages = generateBookPages(BOOK_URL)
    elif MODE == "p":
        print("Checking single page")
        pages = []
        pages.append(pywikibot.Page(site, PAGE_NAME))
    else:
        print("Unknown check mode, exiting")
        exit()

    checkedPages = 0
    errors = 0

    for page in pages:
        if MODE == "r" or MODE == "b":
            page_title = page['title']
        else: #no idea why allpages() does not return pages with [u'title'] as keys 
            page_title = page.title()
        print("" + page_title + "")
        
        page = pywikibot.Page(site, page_title)
        page_url = page.full_url()

        if pywikibot.Category(site,"Structure") in pywikibot.Page(site, page_title).categories():
            print("\tPage " + page_url + " IN 'Structure' category")
            
            if pywikibot.Category(site,"Broken PDF") in pywikibot.Page(site, page_title).categories():
                #if its a structure and has broken pdf, let's remove broken pdf
                print("\tRemoving 'Broken PDF' category from 'Structure' page.")
                pywikibot.Page(site, page_title).change_category(pywikibot.Category(site, "Broken PDF"), None)
            else:
                print("\tPage " + page_url + " NOT IN 'Broken PDF' category")
        
        else:
            # we need to check
            isCheckOK, message = checkPDFforPage(page_url, BASE_SITE)
            if isCheckOK:
                print("\t" + page_title + ": " + message)
                #remove category
                if pywikibot.Category(site,"Broken PDF") in pywikibot.Page(site, page_title).categories():
                    print("\tRemoving 'Broken PDF' category")
                    pywikibot.Page(site, page_title).change_category(pywikibot.Category(site, "Broken PDF"), None)
                    sendTelegramNotification("✅ [" + page_title + "](" + page_url + ") is now ok.")
                else:
                    print("\tNo 'Broken PDF' category to remove. No problem.")
                
            else:
                errors += 1
                print("\t" + page_title + ": " + message)

                #add category if not already broken
                needNotification = addCategory(site, pywikibot.Page(site, page_title), "Broken PDF")

                if needNotification:
                    #notify telegram
                    if MODE == "r":
                        sendTelegramNotification("❌ [" + page_title + "](" + page_url + ") can't be converted to PDF!")
                    if MODE == "b":
                        sendTelegramNotification("❌ [" + page_title + "](" + page_url + ") in [this Book](" + BOOK_URL + ") can't be converted to PDF!")
                
            print("")

            time.sleep(1)

            checkedPages+=1;            

    print("Checked " + str(checkedPages) + " pages")
    print(str(errors) + " checks failed")
    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='PDFCheck Script.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-a", "--all", help="check all pages", dest="modeAll", action="store_true")
    group.add_argument("-r", "--recent", help="check recently edited pages in the last <minutes> minutes", dest="modeRecent", default=None, metavar="<minutes>")
    group.add_argument("-b", "--book", help="check all the pages in a book", dest="modeBook", default=None, metavar="<book_url>")
    group.add_argument("-p", "--page", help="check a single page", dest="modePage", default=None, metavar="<page_name>")
    
    args = parser.parse_args()

    if args.modeAll:
        MODE = "a"
    elif args.modeRecent:
        MODE = "r"
    elif args.modeBook:
        MODE = "b"
    elif args.modePage:
        MODE = "p"

    if MODE == "r":
        DELTATIME = int(args.modeRecent) #in minutes
    else:
        DELTATIME = 0

    if MODE == "b":
        BOOK_URL = args.modeBook
    else:
        BOOK_URL = ""

    if MODE == "p":
        PAGE_NAME = args.modePage
    else:
        PAGE_NAME = ""
    main(MODE, DELTATIME, BOOK_URL, PAGE_NAME)
