import bs4
import logging
import requests
from sparklines import sparklines

# Enable logging
logger = logging.getLogger(__name__)

USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/60.0'
REQUEST_HEADERS = {'User-Agent': USERAGENT}

POLLEN_LOCAL_URL = 'http://www.pollennieuws.nl/owp/pollennieuws/feeds/dailystats-feeder.php?m={}'
POLLEN_COUNTRY_URL = 'http://www.pollennieuws.nl/owp/pollennieuws_2017/feeds/pollen-meldingen.php'


def get_sparklines(bars):
    if not bars:
        return None
    line = []
    for item in bars:
        line.append(item[1])

    sparks = []
    for l in sparklines(line):
        sparks.append(l)
    return sparks


def get_pollen_message(bars):
    """
    bars: {'City1': [...], 'Nederland': [...]}
    groen: "geen last", geel: "weinig last", oranje: "redelijk veel last", rood: "veel last", en paars: "extreem veel last"
    """
    severity = {
        1: "geen last",
        2: "weinig last",
        3: "redelijk veel last",
        4: "veel last",
        5: "extreem veel last"
    }

    message = '<b>Pollenstats:</b>'
    for location in bars:
        message += '\n{}: '.format(location)
        for item in bars[location]:
            if item[1] > 0:
                message += '{} ({}) '.format(severity[item[0]], item[1])
    return message


def get_pollen_graph_message(bars):
    """ Format the pollenstats message with sparkline graphs instead of text and numbers """
    message = '<b>Pollenstats:</b>'
    for location in bars:
        if bars[location]:
            message += '\n{}: 😀{}🤧'.format(location, bars[location][0])
    return message


def get_pollen_stats_for(url):
    logger.debug(url)
    response = requests.get(url, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        return ['Something went wrong while fetching info: {} - {}'.format(response.status_code, response.content)]

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    bars = []
    for counter in range(1, 6):
        expectations = soup.find_all("div", class_="bar{} barLabel barLabelTop".format(counter))
        try:
            bars.append((counter, int(expectations[0].text)))
        except IndexError:
            return None
    return bars


def get_pollen_stats(settings):
    bars = {}
    sparks = {}
    for location in settings.POLLEN_LOCATIONS:
        url = POLLEN_LOCAL_URL.format(location)
        bars[location] = get_pollen_stats_for(url)
        sparks[location] = get_sparklines(bars[location])
    url = POLLEN_COUNTRY_URL
    bars['Nederland'] = get_pollen_stats_for(url)
    sparks['Nederland'] = get_sparklines(bars['Nederland'])

    # Get text-version of message
    #message = get_pollen_message(bars)

    # Get graph-version of message
    message = get_pollen_graph_message(sparks)
    return message
