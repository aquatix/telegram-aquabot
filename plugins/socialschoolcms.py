import hashlib

import bs4
import requests
from pymemcache.client import Client as MemcacheClient

MESSAGE_TTL = 3600 * 25  # Cache messages for 25 hours by default

def get_newsitems(settings):
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

            blok_id = 'aquabot_{}'.format(hashlib.md5(blok_result.encode('utf-8')).hexdigest())
            print(blok_id)
            if not mc.get(blok_id):
                # Only send the message when it was not seen before
                messages.append(blok_result)
            # Cache message
            mc.set(blok_id, blok_result, MESSAGE_TTL)

        return messages

    # No response 200 received
    return ['Something went wrong while fetching info']


def get_agenda(settings):
    """Get agenda items from SocialSchoolCMS for the school defined in settings.py"""
    url = 'http://socialschoolcms.nl/my/website/agenda.php?school=' + settings.SOCIALSCHOOLCMS_SCHOOL

    response = requests.get(url)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        messages = []
        alldivs = soup.find_all("div")
        for div in alldivs:
            if len(div.contents) == 1:
                # It's a header
                messages.append(str(div.contents[0]).replace('<h3>', '<b>').replace('</h3>', '</b>'))
            else:
                item_content = ''
                for part in div.contents:
                    if part:
                        # Sanitise
                        month_content = str(part).replace('<i></i>', '').replace('<br/>', '').strip()
                        # Itemise a bit
                        month_content = month_content.replace('<b>', '\n<b>')

                        if month_content:
                            item_content = item_content + '\n' + month_content
                messages[-1] = messages[-1] + item_content
    return messages
