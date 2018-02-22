TOKEN='ASK_BOTFATHER_FOR_TOKEN'

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
TRELLO_MESSAGE = 'Your tasks for today'
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
