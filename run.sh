#!/bin/bash

sed -i "s/mylang='.*'/mylang='$PYWIKIBOT_LANG'/g" user-config.py
python check.py r 3600
