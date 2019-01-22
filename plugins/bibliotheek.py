from datetime import datetime

import bs4
import requests


def format_books(books):
    """
    Create message
    """
    for book in books:
        print(book['title'])


def get_books_for(username, password, vestnr, cutoff=None):

    s = requests.Session()

    # Get session ID
    r = s.get('https://bicatwww.obbh.nl/cgi-bin/bx.pl?xdoit=y;prt=INTERNET;vestnr=6599;taal=1')
    soup = bs4.BeautifulSoup(r.text, 'html.parser')
    scripts = soup.find_all('script')
    initscript = scripts[1]
    j = str(initscript).split("'sid': ")
    j2 = j[1].rsplit("'")
    sid = j2[1]
    print(sid)

    # Login
    url = 'https://bicatwww.obbh.nl/cgi-bin/bx.pl'
    data = {'newlener': username, 'pinkode': password}
    data['event'] = 'w2a'
    data['vestnr'] = vestnr
    data['action'] = 'loginLocal'
    data['sid'] = sid
    # event: w2a
    # action: loginLocal
    # sid:
    # lener_cookie_vink:
    print(data)

    r = s.post(url, data=data)
    print(r.text)

    response = s.get('https://bicatwww.obbh.nl/cgi-bin/bx.pl?dcat=0;titcode=;medium=;rubplus=;extsdef=;tref=;event=invent;sid={};vestnr={};prt=INTERNET;taal=1;var=portal'.format(sid, vestnr))

    soup = bs4.BeautifulSoup(response.text, 'html.parser')

    # <div id="results">Aantal exemplaren thuis: <span class="totaal">2</span>
    #nr_results = soup.find(id='results')

    date_now = datetime.now()

    books = []

    book_list_items = soup.find_all('li', class_='list_items')
    for book_raw in book_list_items:
        book = {}
        book_item = book_raw.find('div', class_='list_text')
        book['title'] = book_item.find('a', class_='title').text
        book['countdown'] = book_item.find('span', class_='countdown').text
        book['info'] = book_item.find('li').text

        j = str(book['info']).split('Inleverdatum:')
        j2 = j[1].rsplit('|')
        hand_in_str = j2[0].strip()
        hand_in_date = datetime.strptime(hand_in_str, '%Y-%m-%d')
        book['hand_in_date'] = hand_in_date

        delta = hand_in_date - date_now
        book['delta_days'] = delta.days

        if not cutoff or delta.days <= cutoff:
            books.append(book)

    return books
    # https://bicatwww.obbh.nl/cgi-bin/bx.pl?event=w2a;action=haalTitels20Gegevens;items=380745,16730&sid=2858ac0a-772c-4cb3-b140-3f2361a4f36b&vestnr=6525


def get_all_books(settings, cutoff=None):
    books = []
    for member in settings.BIBLIOTHEEK_MEMBERS:
        books.append(get_books_for(member['username'], member['password'], member[' vestnr'], cutoff))

    return format_books(books)
