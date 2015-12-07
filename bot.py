import pywikibot
import requests
import urlparse
from bs4 import BeautifulSoup
import time


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
				return True

			if("error" in status["status"].lower()):
				return status["status"]

			time.sleep(1)
		#print(dom_pdf.find(id='firstHeading'))
	else:
		return "No PDF can be downloaded for this page"


if __name__ == "__main__":
	site = pywikibot.Site()
	pages = site.recentchanges()

	i = 0
	for page in pages:
		page_title = page[u"title"]
		page_url = pywikibot.Page(site, page_title).full_url()

		print("Checking '" + page_title + "'")

		res = checkPage(page_url)
		if(res is True):
			print("\t'" + page_title + "' can be converted to PDF")
		else:
			print("\t'" + page_title + "' - " + res)

		print("")

		i+=1
		if(i==10):
			break
