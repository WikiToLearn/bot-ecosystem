# -*- coding: utf-8 -*-
import os

langs = ['it','en','devit','deven','localit','localen']

#reading variables
mode = os.environ['MODE']
minutes = int(os.environ['MINUTES'])
lang = os.environ['PYWIKIBOT_LANG']

#cheking langs
if not lang in langs:
    print("Lang not supported. Please choose one of:")
    for l in langs:
        print (l)
    exit(1)

#creating config
f = open('user-config.py','w')
f.write('# -*- coding: utf-8 -*-\n')
f.write("mylang='"+ lang+"'\n")
f.write("family='wikitolearn'\n")
f.write("console_encoding = 'utf-8'\n")
f.close()
    
import check

#star process
check.main(mode,minutes)
