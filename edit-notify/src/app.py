#!/usr/bin/env python
import wtl
import wtlpywikibot
import pywikibot
import datetime
import urllib.parse
import time

config = wtl.load_config(config_dir="/etc/edit-notify/")

DELTATIME = config['global']['deltatime']

running = True
time_debit = 0
while running:
    unix_time_start = int(time.time())
    for lang in config['pywikibot']['langs']:
        site = wtlpywikibot.site(lang)
        print(lang)
        recentchanges = site.recentchanges(topOnly=False, end=site.getcurrenttime(
        ) - (datetime.timedelta(seconds=DELTATIME + time_debit)))
        for recentchange in recentchanges:
            change_type = recentchange['type']
            if change_type == 'log':
                change_type = change_type + "-" + \
                    recentchange['logtype'] + "-" + recentchange['logaction']
            title = recentchange['title']
            user = recentchange['user']
            oldlen = recentchange['oldlen']
            newlen = recentchange['newlen']
            revid = recentchange['revid']
            old_revid = recentchange['old_revid']
            comment = recentchange['comment']
            args_page = urllib.parse.urlencode([
                ('title', title)
            ])
            args_rev = urllib.parse.urlencode([
                ('title', title),
                ('revid', revid)
            ])
            args_diff = urllib.parse.urlencode([
                ('title', title),
                ('diff', revid),
                ('oldid', old_revid),
                ('type', 'revision')
            ])
            hostname = site.family.hostname(lang)
            data = {
                "lang": lang,
                "title": title,
                "user": user,
                "oldlen": oldlen,
                "newlen": newlen,
                "revid": newlen,
                "comment": comment,
                "url_page": "//{}/index.php?{}".format(hostname, args_page),
                "url_rev": "//{}/index.php?{}".format(hostname, args_rev),
                "url_diff": "//{}/index.php?{}".format(hostname, args_diff)
            }
            if change_type == "log-move-move" or change_type == "move-move_redir":
                data['target_title'] = recentchange['logparams']['target_title']
                args_target_page = urllib.parse.urlencode([
                    ('title', data['target_title'])
                ])
                data["url_target_page"] = "//{}/index.php?{}".format(hostname, args_target_page)
            elif change_type == "rights-rights":
                newgroups = recentchange['logparams']['newgroups']
                oldgroups = recentchange['logparams']['oldgroups']
                data['newgroups'] = newgroups
                data['oldgroups'] = oldgroups
                # example for
                # 'logparams': {
                #  'newgroups': ['bot', 'bureaucrat', 'sysop', 'suppress'],
                #  'oldgroups': ['bot', 'bureaucrat', 'sysop']
                # },
            wtl.send_notify(data, change_type, config['gateway'])
            if change_type == "new" or change_type == "edit":
                try:
                    page = pywikibot.Page(site, title)
                    if wtlpywikibot.get_category_status(site, page, "ReadyToBePublished"):
                        wtl.send_notify(
                            data, "readytobepublished", config['gateway'])
                except Exception as e:
                    print(e)
    unix_time_end = int(time.time())
    waiting_time = DELTATIME - (unix_time_end - unix_time_start)
    if waiting_time > 0:
        print("Wait for: {} s".format(waiting_time))
        for s in range(0, DELTATIME - (unix_time_end - unix_time_end)):
            time.sleep(1)
        time_debit = 0
    else:
        time_debit = -1 * waiting_time
