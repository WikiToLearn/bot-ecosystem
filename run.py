# -*- coding: utf-8 -*-
import os

langs = ['it','en','devit','deven','localit','localen']

#reading lang
lang = os.environ.get(['PYWIKIBOT_LANG'])

#cheking langs
if not lang in langs:
    print("Lang not supported. Please choose one of:")
    print ('Production: it,en.')
    print ('Testing: devit,deven.')
    print ('Local: localit,localen.')
    exit(1)
    
#reading other pars
MODE = os.environ.get(['MODE'])
MINUTES = int(os.environ.get(['MINUTES']) or "0")
BOOK_URL = os.environ.get(['BOOK_URL'])
PAGE_NAME = os.environ.get(['PAGE_NAME'])

#creating config
f = open('user-config.py','w')
f.write('# -*- coding: utf-8 -*-\n')
f.write("mylang='"+ lang+"'\n")
f.write("family='wikitolearn'\n")
f.write("console_encoding = 'utf-8'\n")
f.write("""password_file = "./passwordFile.txt"
            usernames = {}
            usernames[family] = {}
            usernames[family][mylang] = u"WikiToBot"
        """);
f.close()
    
import check

#star process
check.main(MODE, MINUTES, BOOK_URL, PAGE_NAME)
