#!/bin/bash

docker run -ti -e PYWIKIBOT_LANG=$1 -e PASSWORD=$2 -e MODE=$3 -e MINUTES=$4 -e TG_CHAT_ID="@wtlpdfcheck" -e TG_API_KEY=$5 \
    -e BOOK_URL=$6 -e PAGE_NAME=$6   wikitolearn/pdfcheck:0.2
