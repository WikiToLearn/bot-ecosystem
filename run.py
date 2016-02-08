# -*- coding: utf-8 -*-
import os

langs = ['it','en','devit','deven','localit','localen']

#reading lang
lang = os.environ.get('PYWIKIBOT_LANG')

#cheking langs
if not lang in langs:
    print("Lang not supported. Please choose one of:")
    print ('Production: it,en.')
    print ('Testing: devit,deven.')
    print ('Local: localit,localen.')
    exit(1)
    
#reading other pars
MODE = os.environ.get('MODE')
MINUTES = int(os.environ.get('MINUTES') or "0")
BOOK_URL = os.environ.get('BOOK_URL')
PAGE_NAME = os.environ.get('PAGE_NAME')
PASSWORD = os.environ.get('PASSWORD')

#creating config
f = open('user-config.py','w')
f.write('# -*- coding: utf-8 -*-\n')
f.write("mylang='"+ lang+"'\n")
f.write("family='wikitolearn'\n")
f.write("console_encoding = 'utf-8'\n")
f.write('password_file = "./passwordFile.txt"\n')
f.write('usernames = {}\n')
f.write('usernames[family] = {}\n')
f.write('usernames[family][mylang] = u"WikiToBot"\n')
f.close()

#creating password_file
p = open('passwordFile.txt','w')
p.write('("WikiToBot", "'+ PASSWORD +'")\n')
p.close()
    
import check

#star process
check.main(MODE, MINUTES, BOOK_URL, PAGE_NAME)
