# Telegram API
TOKEN='ASK_BOTFATHER_FOR_TOKEN'

# Message telling there's nothing for this instance
FALLBACK_MESSAGE = 'N/A'

# http://socialschoolcms.nl/my/website/mededelingen.php?school=URL_TOKEN
SOCIALSCHOOLCMS_SCHOOL='URL_TOKEN'

# By default, don't send to multiple persons
SEND_TO = None
# Use https://telegram.me/userinfobot to get the user ID's to send updates to
# SEND_TO = [
#     42,  # @TheAnswer
#     0,  # @Root
# ]

FEEDS = [
    'https://example.com/feed.xml',  # Some news feed
    'https://example.com/subsite/feed.xml',  # Some other feed
]

TRELLO_APIKEY = ''
TRELLO_TOKEN = ''
TRELLO_BOARD = 'Tasks'
TRELLO_HEADER = 'Your tasks for today'
TRELLO_HEADER_TOMORROW = 'Forecast this 🌆 for {}:'
TRELLO_MESSAGE = 'No tasks for today, go wild!'
TRELLO_INITIALS_TO_TELEGRAM = {
    'AB': 12345678,
    'BC': 42424242,
}

# 0 = Monday
WEEKDAY_NAMES = [
    'Maandag',
    'Dinsdag',
    'Woensdag',
    'Donderdag',
    'Vrijdag',
    'Zaterdag',
    'Zondag',
]

# Get the location from the sidebar at http://www.pollennieuws.nl/
POLLEN_LOCATIONS = [
    '',  # E.g., 'Amsterdam' or 'Haarlem'
]

# DARKSKY_APIKEY = ''
# DARKSKY_LAT =
# DARKSKY_LON =
