import datetime
import logging

from trello import TrelloClient
from trello.exceptions import Unauthorized

logger = logging.getLogger(__name__)

def get_today(settings):
    """Get today's name"""
    weekday = datetime.datetime.today().weekday()
    # 0 = Monday
    return settings.WEEKDAY_NAMES[weekday]


def get_tomorrow(settings):
    """Get tomorrow's name"""
    tomorrow = datetime.datetime.today() + datetime.timedelta(days=1)
    weekday = tomorrow.weekday()
    # 0 = Monday
    return settings.WEEKDAY_NAMES[weekday]


def get_board_with_name(boards, name):
    for board in boards:
        if board.name == name:
            return board


def lists_to_lists(client, board):
    """Get all lists with their cards from board `board`"""
    members = {}
    lists = []
    for this_list in board.list_lists():
        items = []
        for card in this_list.list_cards():
            names = []
            for member in card.member_ids:
                if member in members:
                    names.append(members[member])
                else:
                    names.append(client.get_member(member))
            items.append((card.name, names))
        lists.append((this_list.name, items))
    return lists


def get_list(client, board, name):
    """Return list of cards from `board` from the list `name`"""
    members = {}
    items = []
    for this_list in board.list_lists():
        if this_list.name == name:
            for card in this_list.list_cards():
                names = []
                for member in card.member_ids:
                    if not member in members:
                        # Cache this user
                        members[member] = client.get_member(member)
                    names.append(members[member].initials)
                if not names:
                    # Fall back to 'everyone'
                    names = ['👪']
                items.append({'name': card.name, 'members': names})
            return items
    return items


def list_to_memberslist(settings, this_list):
    memberslists = {}
    for member in settings.TRELLO_INITIALS_TO_TELEGRAM:
        memberslists[member] = []
    memberslists['all'] = []

    for item in this_list:
        for member in item['members']:
            memberslists[member].append(item['name'])
        if not item['members']:
            memberslists['all'].append(item['name'])

    return memberslists


def list_to_message(this_list):
    message = '\n'.join(['<li>{}</li>'.format(item) for item in this_list])
    return message


def memberslist_to_messages(memberslists):
    result = {}
    for member in memberslists:
        result[member] = list_to_message(memberslists[member])
    return result


def cardlist_to_message(settings, this_list, header):
    if this_list:
        message = '\n'.join(['{members}: {desc}'.format(members=', '.join(item['members']), desc=item['name']) for item in this_list])
    else:
        message = settings.TRELLO_MESSAGE
    message = '*{}*\n{}'.format(header, message)
    return message


def get_planning_for(settings, for_day, header):
    """Get the planning items for specified day"""
    client = TrelloClient(api_key=settings.TRELLO_APIKEY, token=settings.TRELLO_TOKEN)

    try:
        all_boards = client.list_boards()
    except Unauthorized:
        return 'Geen toegang tot Trello'

    board_for_listing = get_board_with_name(all_boards, settings.TRELLO_BOARD)
    the_day_list = get_list(client, board_for_listing, for_day)
    logger.debug(the_day_list)
    #memberslist = list_to_memberslist(settings, the_day_list)
    message = cardlist_to_message(settings, the_day_list, header)
    logger.debug(message)
    return message


def get_todays_planning(settings):
    today = get_today(settings)
    header = settings.TRELLO_HEADER
    return get_planning_for(settings, today, header)


def get_tomorrows_planning(settings):
    tomorrow = get_tomorrow(settings)
    header = settings.TRELLO_HEADER_TOMORROW.format(tomorrow)
    return get_planning_for(settings, tomorrow, header)
