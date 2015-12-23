import pywikibot
import requests
import urlparse
from bs4 import BeautifulSoup
import time
import datetime
import sys

config = __import__("user-config")

##Telegram Stuff
TG_API_KEY = "178647524:AAG7hkTnFLU1x7nRYqhGQAemxPsloUbj9ik"
TG_CHAT_ID = "@wtlpdfcheck"

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
	    print e
	    sys.exit(1)


if __name__ == "__main__":
	
	print("Connecting to " + config.mylang + " domain for the " + config.family + " family")
	site = pywikibot.Site()

	BASE_SITE = site.family.langs[config.mylang]
	print("Base URL: " + BASE_SITE)

	MODE = sys.argv[1].lower() #"r" for recent or "a" for all 
	if MODE == "r":
		print("Checking most recent edits")
		DELTATIME = int(sys.argv[2]) #in minutes
		pages = site.recentchanges(topOnly = True, end=site.getcurrenttime()- datetime.timedelta(minutes=DELTATIME))
	else:
		print("Checking all pages")
		pages = site.allpages()

	checkedPages = 0
	errors = 0

	for page in pages:
		if MODE == "r":
			page_title = page[u'title'].encode('utf8')
		else: #no idea why allpages() does not return pages with [u'title'] as keys 
			page_title = page.title().encode('utf8')
		print("" + page_title + "")

		page_url = pywikibot.Page(site, page_title).full_url()
		
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

		print("")

		time.sleep(1)

		checkedPages+=1;

	print("Checked " + str(checkedPages) + " pages")
	print(str(errors) + " checks failed")