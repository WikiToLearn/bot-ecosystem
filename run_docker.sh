#!/bin/bash

docker run -dti -e PYWIKIBOT_LANG=$1 -e MODE=$2 -e MINUTES=$3 -e TG_CHAT_ID="@wtlpdfcheck" -e TG_API_KEY=$4 --name pdfcheck  wikitolearn/pdfcheck:0.1
