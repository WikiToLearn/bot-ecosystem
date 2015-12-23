#!/bin/bash

sed -i "s/mylang='.*'/mylang='$PYWIKIBOT_LANG'/g" user-config.py
echo '*/$INTERVAL * * * * sh /pywikibot/run.sh'> /etc/crontab
python check.py r $MINUTES
