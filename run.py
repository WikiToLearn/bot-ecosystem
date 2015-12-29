# -*- coding: utf-8 -*-
import os

langs = ['it','en','devit','deven','localit','localen']

#reading lang
lang = os.environ['PYWIKIBOT_LANG']

#cheking langs
if not lang in langs:
    print("Lang not supported. Please choose one of:")
    print ('Production: it,en.')
    print ('Testing: devit,deven.')
    print ('Local: localit,localen.')
    exit(1)
    
#reading other pars
mode = os.environ['MODE']
minutes = int(os.environ['MINUTES'])

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
