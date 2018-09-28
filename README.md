# telegram-aquabot

Telegram bot to provide information from various sources, like SocialSchoolCMS for news items and agenda, Trello for weekday items, pollen information (for The Netherlands), and sunrise, sunset and moon phase information, provided by [DarkSky](https://darksky.net/dev).

Created because I wanted to have the information come to me instead of having to go and look at a small info frame on a school's website. Also, Telegram is pretty cool.

Uses [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) and some [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/) to make sense of some awful HTML.


## Commands

```
/schoolagenda - fetches the agenda of your configured school and posts messages per month

/reminder <seconds> <message> - set reminder for yourself
/remindall <seconds> <message> - set reminder for all users configured to get news items (SEND_TO)
```


## Installation

[Get yourself a bot configured](https://github.com/python-telegram-bot/python-telegram-bot/wiki/Introduction-to-the-API) with the [BotFather](https://telegram.me/botfather).

Create a (Python 3) virtualenv (`mkvirtualenv -p /usr/bin/python3 aquabot`) and `pip install -r requirements.txt`. Copy settings.example.py to settings.py and edit TOKEN to the token you got from the BotFather. Set a SocialSchoolCMS school identifier if you want and configure some Telegram ID's for the users that want to receive those updates. You can get your ID by talking with [userinfobot](https://telegram.me/userinfobot).

See [settings.example.py](settings.example.py) for the other configuration options (for Trello, pollen, DarkSky).
