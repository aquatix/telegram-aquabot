import requests
import bs4

def get_contents(settings):
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
            messages.append(blok_result)

        return messages
        result = '\n'.join(messages)
        return result
    return url
