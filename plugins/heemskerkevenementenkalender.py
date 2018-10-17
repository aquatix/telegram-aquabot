from datetime import date, timedelta

import bs4
import requests


def format_calendar_item(item):
    if item[1]:
        # Item has a time window
        return '<b>{}</b> {}: {} (locatie: {})\n'.format(item[0], item[1], item[2], item[3])
    return '<b>{}</b>: {} (locatie: {})\n'.format(item[0], item[2], item[3])


def get_event_items():
    url = 'https://www.heemskerk.nl/melden-en-meedoen/evenementenkalender/'
    response = requests.get(url)

    if response.status_code == requests.codes.ok:
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        calendar_tables = soup.find_all('table', {'class': 'ce-table'})
        cal_items = []
        for month in calendar_tables:
            items = month.find_all('tr')
            for item in items:
                pieces = item.find_all('td')
                cal_item = []
                skip_item = False
                for piece in pieces:
                    if piece.get_text().strip() == 'Datum':
                        skip_item = True
                    cal_item.append(piece.get_text().strip())
                if not skip_item:
                    cal_items.append(cal_item)
    return cal_items


def filter_items_for_date(items, datestamp):
    result = []
    for item in items:
        if item[0] == datestamp:
            result.append(item)
    return result


def get_items_for_today_and_tomorrow():
    all_items = get_event_items()
    today = date.today()
    tomorrow = today + timedelta(1)
    today_stamp = '{:02d}-{:02d}-{}'.format(today.day, today.month, today.year)
    tomorrow_stamp = '{:02d}-{:02d}-{}'.format(tomorrow.day, tomorrow.month, tomorrow.year)
    todays_items = filter_items_for_date(all_items, today_stamp)
    tomorrows_items = filter_items_for_date(all_items, tomorrow_stamp)
    print(todays_items)
    print(tomorrows_items)

    message = ''
    for item in todays_items:
        message += format_calendar_item(item)
    for item in tomorrows_items:
        message += format_calendar_item(item)

    if message:
        message = 'Evenementen:\n{}'.format(message)

    print(message)
    return message


if __name__ == '__main__':
    get_items_for_today_and_tomorrow()
