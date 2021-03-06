import datetime
import hashlib
import logging
import unicodedata

import bs4
import requests
from pymemcache.client import Client as MemcacheClient

# Enable logging
logger = logging.getLogger(__name__)

MESSAGE_TTL = 3600 * 25  # Cache messages for 25 hours by default
USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/60.0'
REQUEST_HEADERS = {'User-Agent': USERAGENT}

def get_newsitems(settings):
    """Get news items from SocialSchoolCMS for the school defined in settings.py

    :param: settings: project settings
    :return: list with current news items
    :rtype: list
    """
    # Items get cached in memcached
    mc = MemcacheClient(('127.0.0.1', 11211))

    url = 'http://socialschoolcms.nl/app/5/announcements.php?school_id={}'.format(settings.SOCIALSCHOOLCMS_SCHOOL)

    response = requests.get(url, headers=REQUEST_HEADERS)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')

        messages = []

        alldivs = soup.find_all("div", class_="row")
        for div in alldivs:
            notice_divs = div.find_all("div", class_="col-md-4")
            for notice_div in notice_divs:
                notice = str(notice_div.contents[0]).replace('<div class="content-block">', '').replace('<p>', '').replace('</p>', '\n').replace('<br/>', '\n').replace('</div>', '').strip()

                notice_id = 'aquabot_{}'.format(hashlib.md5(notice.encode('utf-8')).hexdigest())
                logger.debug(notice_id)
                # Normalise string characters (for example changing nbsp \xa0 into regular space)
                notice = unicodedata.normalize("NFKD", notice)
                if not mc.get(notice_id):
                    # Only send the message when it was not seen before
                    logger.debug('cache miss for %s', notice_id)
                    messages.append(notice)
                if not settings.DEBUG:
                    # Cache message (only when not debugging)
                    mc.set(notice_id, notice, MESSAGE_TTL)

        return messages

    # No response 200 received
    return ['Something went wrong while fetching info: {} - {}'.format(response.status_code, response.content)]


def get_agenda(settings):
    """Get agenda items per month from SocialSchoolCMS for the school defined in settings.py

    :param: settings: project settings
    :return: list with agenda per month
    :rtype: list
    """
    url = 'http://socialschoolcms.nl/my/website/agenda.php?school=' + settings.SOCIALSCHOOLCMS_SCHOOL

    messages = []
    response = requests.get(url, headers=REQUEST_HEADERS)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        alldivs = soup.find_all("div")
        for div in alldivs:
            if len(div.contents) == 1:
                # It's a header
                messages.append(
                    unicodedata.normalize("NFKD", str(div.contents[0]).replace('<h3>', '<b>').replace('</h3>', '</b>'))
                )
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
                messages[-1] = messages[-1] + unicodedata.normalize("NFKD", item_content)
    return messages


def get_week_agendas(settings):
    """Get agenda items from SocialSchoolCMS for the school defined in settings.py

    :param: settings: project settings
    :return: list of weeks, each as a tuple with week number and agenda for that week
    :rtype: list
    """
    url = 'http://socialschoolcms.nl/app/5/calendar.php?school_id=' + settings.SOCIALSCHOOLCMS_SCHOOL

    weeks = []
    response = requests.get(url)
    if response.status_code == 200:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        alldivs = soup.find_all("div", class_="row")
        for div in alldivs:
            weekdivs = div.find_all("div", class_="col-md-4")
            for weekdiv in weekdivs:
                week = weekdiv.contents[0].text
                content = str(weekdiv.contents[1]).replace('<div class="content-block">', '').replace('<div class="sep"></div>', '').replace('</div>', '')
                content = content.replace('<strong class="dag">', '<b>').replace('</strong>', '</b>').replace('<br/>', '\n')
                # Add heading
                content = '<b>Agenda {}:</b>\n{}'.format(week, content)
                weeks.append((week, unicodedata.normalize("NFKD", content)))
    return weeks


def get_thisweeks_agenda(settings):
    """Gets agenda items for this week only

    :param: settings: project settings
    :return: message tuple with the agenda for the current week
    :rtype: tuple
    """
    all_agendas = get_week_agendas(settings)
    this_week_number = datetime.date.today().isocalendar()[1]
    for week in all_agendas:
        if week[0] == 'Week {}'.format(this_week_number):
            return week
    # Nothing for this week, tell so
    return (
        'Week {}'.format(this_week_number),
        '<b>Agenda Week {}:</b>\n{}'.format(this_week_number, settings.FALLBACK_MESSAGE)
    )
