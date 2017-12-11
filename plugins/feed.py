import hashlib
from time import mktime, strftime

import feedparser
from pymemcache.client import Client as MemcacheClient

MESSAGE_TTL = 3600 * 25  # Cache messages for 25 hours by default

def format_newsitem(item):
    clean_content = item['content'].replace('<p>', '').replace('</p>', '\n').replace('&nbsp;', ' ')
    return '<b>{}</b>\n<i>{}</i>\n\n{}'.format(item['title'], item['updated'], clean_content)


def get_feedupdates(settings):
    # Items get cached in memcached
    mc = MemcacheClient(('127.0.0.1', 11211))

    result = []
    for url in settings.FEEDS:
        d = feedparser.parse(url)
        feed_key = hashlib.md5(url.encode('utf-8')).hexdigest()

        everyitem = []
        everything = {}
        for entry in d.entries:
            pretty_timestamp = strftime('%Y-%m-%d %H:%M', entry.updated_parsed)
            timestamp = int(mktime(entry.updated_parsed))
            everyitem.append(timestamp)
            everything[timestamp] = {'updated': pretty_timestamp, 'title': entry.title, 'content': entry.content[0].value}

        everyitem.sort()
        latest = everyitem[-2:]

        for item in latest:
            newsitem = format_newsitem(everything[item])
            update_id = 'aquabot_{}_{}'.format(feed_key, hashlib.md5(newsitem.encode('utf-8')).hexdigest())
            print(update_id)
            if not mc.get(update_id):
                result.append(newsitem)
            # Cache message
            mc.set(update_id, newsitem, MESSAGE_TTL)

    return result
