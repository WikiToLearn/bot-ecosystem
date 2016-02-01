import pywikibot
import requests
import urllib.parse as urlparse
from bs4 import BeautifulSoup
import time
import datetime
import sys
import os
config = __import__("user-config")

##Telegram Stuff
TG_API_KEY = os.environ['TG_API_KEY']
TG_CHAT_ID = os.environ['TG_CHAT_ID']

BASE_SITE = ""

def checkPage(page_url):
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

def main(MODE,DELTATIME):	
	print("Connecting to " + config.mylang + " domain for the " + config.family + " family")
	site = pywikibot.Site()
	
	global BASE_SITE
	BASE_SITE = site.family.langs[config.mylang]
	print("Base URL: " + BASE_SITE)
	
	if MODE == "r":
		print("Checking most recent edits")
		pages = site.recentchanges(topOnly = True, end=site.getcurrenttime()- datetime.timedelta(minutes=DELTATIME))
	else:
		print("Checking all pages")
		pages = site.allpages()

	checkedPages = 0
	errors = 0

	for page in pages:
		if MODE == "r":
			page_title = page[u'title']
		else: #no idea why allpages() does not return pages with [u'title'] as keys 
			page_title = page.title()
		print("" + page_title + "")

		page_url = pywikibot.Page(site, page_title).full_url()
		
		needsCheck = true
		for cat in pywikibot.Page(site, page_title).categories():
			needsCheck = cat != pywikiBot.Category("Structure")
			if not needsCheck: 
				break
		
		if needsCheck:
			
			isCheckOK, message = checkPage(page_url)
			if isCheckOK:
				print("\t" + page_title + ": " + message)
			else:
				errors+=1
				print("\t" + page_title + ": " + message)
				payload = { 'chat_id': TG_CHAT_ID, 
							'text': "[" + page_title + "](" + page_url + ") can't be converted to PDF!",
							'parse_mode': 'Markdown' }

				#notify telegram
				if MODE == "r":
					requests.get("https://api.telegram.org/bot" + TG_API_KEY + "/sendmessage", params=payload)
					
				pywikibot.Page(site, page_title).change_category(None, pywikibot.Category(site, "Broken PDF"))
				
			print("")

			time.sleep(1)

			checkedPages+=1;
		else:
			print("Page " + page_url + " in structure category")

	print("Checked " + str(checkedPages) + " pages")
	print(str(errors) + " checks failed")
	

if __name__ == "__main__":
        MODE = sys.argv[1].lower() #"r" for recent or "a" for all 
        DELTATIME = int(sys.argv[2]) #in minutes
        main(MODE,DELTATIME)
