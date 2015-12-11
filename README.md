# PDFCheck

Very Work In Progress

## Setup

* Clone/Download this repo
* Install pip and  virtualenv
* cd into this repo
* virtualenv venv
* source venv/bin/activate 
* pip install -r  requirements.txt
* copy wikitolearn_family.py to 'venv/lib/python2.7/site-packages/pywikibot/families'
* edit
* python bot.py <r|a> [minutes]
	* r if you want to scan recent pages
		* also pass 'minutes', pages changed in the last 'minutes' minutes will be checked
	* a if you want to scan all scannable pages   