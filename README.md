# PDFCheck

For Python 3

## Setup

* Clone/Download this repo
* Install `pip` and `virtualenv`
* `cd` into this repo
* `virtualenv -p /usr/bin/python3 venv`
* `source venv/bin/activate `
* `pip install -r  pdfchech_requirements.txt`
* copy `wikitolearn_family.py` to `venv/lib/python*/site-packages/pywikibot/families`
* set `TG_API_KEY` and `TG_CHAT_ID` env variables
* `python bot.py <r|a> [minutes]`
	* `r` if you want to scan recent pages
		* also pass `minutes`, pages changed in the last 'minutes' minutes will be checked
	* `a` if you want to scan all scannable pages   