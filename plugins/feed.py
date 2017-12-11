from time import mktime, strftime

import feedparser


def get_feedupdates(url):
    d = feedparser.parse(url)

    everyitem = []
    everything = {}
    for entry in d.entries:
        dPubPretty = strftime('%Y-%m-%d %H:%M', entry.updated_parsed)
        dPubStamp = int(mktime(entry.updated_parsed))
        everyitem.append(dPubStamp)
        everything[dPubStamp] = {'updated': dPubPretty, 'title': entry.title, 'content': entry.content[0].value}

    everyitem.sort()
    latest = everyitem[-2:]

    result = []
    for item in latest:
        result.append(everything[item])
    return result
