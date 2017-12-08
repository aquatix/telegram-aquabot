import hashlib

import bs4
import requests
from pymemcache.client import Client as MemcacheClient

MESSAGE_TTL = 3600 * 25  # Cache messages for 25 hours by default

def get_contents(settings):
    """Get news items from SocialSchoolCMS for the school defined in settings.py"""
    # Items get cached in memcached
    mc = MemcacheClient(('127.0.0.1', 11211))

    url = 'http://socialschoolcms.nl/my/website/mededelingen.php?school=' + settings.SOCIALSCHOOLCMS_SCHOOL

    response = requests.get(url)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        bloks = soup.find_all("div", class_="blok")
        messages = []
        for blok in bloks:
            blok_result = ''
            for paragraph in blok.find_all('p'):
                blok_result = blok_result + str(paragraph).replace('<p>', '').replace('</p>', '\n').strip()

            blok_hash = hashlib.md5(blok_result.encode('utf-8')).hexdigest()
            print(blok_hash)
            if not mc.get(blok_hash):
                # Only send the message when it was not seen before
                messages.append(blok_result)
            # Cache message
            mc.set(blok_hash, blok_result, MESSAGE_TTL)

        return messages

    # No response 200 received
    return ['Something went wrong while fetching info']
