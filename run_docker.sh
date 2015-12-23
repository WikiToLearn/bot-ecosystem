#!/bin/bash

docker run -ti -e PYWIKIBOT_LANG=$1 -e MINUTES=$2 -e INTERVAL=$3 --name pdfcheck --rm wikitolearn/pdfcheck:0.1
