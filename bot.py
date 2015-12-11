import pywikibot
import requests
import urlparse
from bs4 import BeautifulSoup
import time
import datetime
import sys

##Telegram Stuff
TG_API_KEY = ""
TG_CHAT_ID = ""

def checkPage(page_url):
	headers = {
		'User-Agent': 'PDF Bot - WikiToLearn'
	}
	r = requests.get(page_url, headers=headers)

	dom = BeautifulSoup(r.text, 'html.parser')

	li_pdf = dom.find(id="coll-download-as-rdf2latex")
	if li_pdf:
		a_pdf = li_pdf.find('a').get('href')
		r_pdf = requests.head("http://it.tuttorotto.eu" + a_pdf, headers=headers, allow_redirects=True)
		
		par = urlparse.parse_qs(urlparse.urlparse(r_pdf.url).query)
		collection_id = par['collection_id'][0]

		url_check = "http://it.tuttorotto.eu/index.php?action=ajax&rs=wfAjaxGetMWServeStatus&rsargs%5B%5D=" + collection_id + "&rsargs%5B%5D=rdf2latex";
		
		while True:
			r_checkStatus = requests.get(url_check, headers=headers)
			status = r_checkStatus.json()[u"status"]

			if(status["progress"] == "100.00"):
				return True, "Converted to PDF"

			if("error" in status["status"].lower()):
				return False, status["status"]

			time.sleep(1)
	else:
		return True, "No PDF can be downloaded for this page"



if __name__ == "__main__":

	MODE = sys.argv[1].lower() #"r" for recent or "a" for all 

	site = pywikibot.Site()
	if MODE == "r":
		DELTATIME = int(sys.argv[2]) #in minutes
		pages = site.recentchanges(topOnly = True, end=site.getcurrenttime()- datetime.timedelta(minutes=DELTATIME))
	else:
		pages = site.allpages()

	i = 0
	for page in pages:
		if MODE == "r":
			page_title = page[u'title']
		else: #no idea why allpages() does not return pages with [u'title'] as keys 
			page_title = page.title()
		page_url = pywikibot.Page(site, page_title).full_url()

		print("Checking '" + page_title + "'")

		valid, message = checkPage(page_url)
		if(valid is True):
			print("\t" + page_title + ": " + message)
		else:
			print("\t" + page_title + ": " + message)
			payload = { 'chat_id': TG_CHAT_ID, 
						'text': "[" + page_title + "](" + page_url + ") can't be converted to PDF!",
						'parse_mode': 'Markdown' }

			requests.get("https://api.telegram.org/bot" + TG_API_KEY + "/sendmessage", params=payload);

		print("")

		time.sleep(1)

		i+=1;

	print("Scanned " + str(i) + " pages")
