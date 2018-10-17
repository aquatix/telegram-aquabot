import bs4
import requests

from datetime import date, timedelta


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
                    print(cal_item)
                    cal_items.append(cal_item)
    return cal_items


def filter_items_for_date(items, date):
    result = []
    for item in items:
        if item[0] == date:
            result.append(item)
    return result


def get_items_for_today_and_tomorrow():
    all_items = get_event_items()
    today = date.today()
    tomorrow = today + timedelta(1)
    today_stamp = '{:02d}-{:02d}-{}'.format(today.day, today.month, today.year)
    tomorrow_stamp = '{:02d}-{:02d}-{}'.format(tomorrow.day, tomorrow.month, tomorrow.year)
    print(today_stamp)
    print(tomorrow_stamp)
    todays_items = filter_items_for_date(today_stamp, all_items)
    tomorrows_items = filter_items_for_date(tomorrow_stamp, all_items)
    print(todays_items)
    print(tomorrows_items)


if __name__ == '__main__':
    get_items_for_today_and_tomorrow()
