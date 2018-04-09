import bs4
import requests

USERAGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/60.0'
REQUEST_HEADERS = {'User-Agent': USERAGENT}

POLLEN_URL = 'http://www.pollennieuws.nl/owp/pollennieuws/feeds/dailystats-feeder.php?m={}'


def get_pollen_message(bars):
    """ groen: "geen last", geel: "weinig last", oranje: "redelijk veel last", rood: "veel last", en paars: "extreem veel last" """
    severity = {
        1: "geen last",
        2: "weinig last",
        3: "redelijk veel last",
        4: "veel last",
        5: "extreem veel last"
    }

    message = '<b>Pollenstats:</b>\n'
    for item in bars:
        if item[1] > 0:
            message += '{} {}'.format(severity[item[0]], item[1])
    return message


def get_pollen_stats(settings):
    url = POLLEN_URL.format(settings.POLLEN_LOCATION)

    response = requests.get(url, headers=REQUEST_HEADERS)
    if response.status_code != 200:
        return ['Something went wrong while fetching info: {} - {}'.format(response.status_code, response.content)]

    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    bars = []
    for counter in range(1, 6):
        #expectations = soup.find_all("div", ["bar{}".format(counter), "barLabel"])
        expectations = soup.find_all("div", class_="bar{} barLabel barLabelTop".format(counter))
        print(expectations[0].text)

        bars.append((counter, int(expectations[0].text)))

    print(bars)
    message = get_pollen_message(bars)
    print(message)
    return message
