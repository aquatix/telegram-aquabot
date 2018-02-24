import bs4
import datetime
import logging
import requests

from trello import TrelloClient

logger = logging.getLogger(__name__)

def get_today(settings):
    """Get today's name"""
    weekday = datetime.datetime.today().weekday()
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
    for this_list in board.list_lists():
        items = []
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


def cardlist_to_message(settings, this_list):
    if this_list:
        message = '\n'.join(['{members}: {desc}'.format(members=', '.join(item['members']), desc=item['name']) for item in this_list])
    else:
        message = settings.TRELLO_MESSAGE
    message = '*{}*\n{}'.format(settings.TRELLO_HEADER, message)
    return message


def get_todays_planning(settings):
    """Get the planning items for today"""
    client = TrelloClient(api_key=settings.TRELLO_APIKEY, token=settings.TRELLO_TOKEN)

    all_boards = client.list_boards()

    board_for_listing = get_board_with_name(all_boards, settings.TRELLO_BOARD)
    today_list = get_list(client, board_for_listing, get_today(settings))
    logger.debug(today_list)
    #memberslist = list_to_memberslist(settings, today_list)
    message = cardlist_to_message(settings, today_list)
    logger.debug(message)
    return message