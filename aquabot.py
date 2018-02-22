#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages, set timers and provide updates.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Give periodic updates from various sources. Set reminder message with timer.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import datetime
import logging
from uuid import uuid4

from telegram import (InlineQueryResultArticle, InputTextMessageContent,
                      ParseMode)
from telegram.ext import (CommandHandler, Filters, InlineQueryHandler,
                          MessageHandler, Updater)
from telegram.utils.helpers import escape_markdown

import settings
from plugins import feed, socialschoolcms, trello

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi! Use /set <seconds> to set a timer')


def help(bot, update):
    """Send a message when the command /help is issued."""
    update.message.reply_text('You can type \'/schoolagenda\' to get the upcoming events, or set a reminder for yourself with /reminder <seconds> <message>, or for all configured users by /remindall <seconds> <message>. Selected users will get automatic notifications about news.')


def send_reminder(bot, job):
    """Send the reminder message."""
    bot.send_message(job.context['user_id'], text='Reminder: {}'.format(job.context['message']))


def set_reminder(bot, update, args, job_queue, chat_data, to_all=False):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Reconstruct the message from the splitted input
        message = ' '.join(args[1:])

        if to_all:
            for user_id in settings.SEND_TO:
                # Add job to queue
                job = job_queue.run_once(send_reminder, due, context={'user_id': user_id, 'message': message})
                logger.info('Setting reminder (remindall) for %s by %s', user_id, chat_id)
                chat_data['remindall_job_{}'.format(user_id)] = job
        else:
            # Add job to queue
            job = job_queue.run_once(send_reminder, due, context={'user_id': chat_id, 'message': message})
            logger.info('Setting reminder for %s by %s', chat_id, chat_id)
            chat_data['reminder_job_{}'.format(chat_id)] = job

        update.message.reply_text('Reminder successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /reminder <seconds> <message>')


def set_remindall(bot, update, args, job_queue, chat_data):
    set_reminder(bot, update, args, job_queue, chat_data, to_all=True)


def unset(bot, update, chat_data):
    """Remove the job if the user changed their mind."""
    if 'job' not in chat_data:
        update.message.reply_text('You have no active timer')
        return

    job = chat_data['job']
    job.schedule_removal()
    del chat_data['job']

    update.message.reply_text('Timer successfully unset!')


def inlinequery(bot, update):
    """Handle the inline query."""
    query = update.inline_query.query
    results = [
        InlineQueryResultArticle(
            id=uuid4(),
            title="Caps",
            input_message_content=InputTextMessageContent(
                query.upper())),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Bold",
            input_message_content=InputTextMessageContent(
                "*{}*".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN)),
        InlineQueryResultArticle(
            id=uuid4(),
            title="Italic",
            input_message_content=InputTextMessageContent(
                "_{}_".format(escape_markdown(query)),
                parse_mode=ParseMode.MARKDOWN))]

    update.inline_query.answer(results)


def send_response(bot, update):
    """Handle the inline query."""
    query = update.message.text
    theresult = "_{}_".format(escape_markdown(query))

    bot.send_message(chat_id=update.message.chat_id, text=theresult)


def check_socialschoolcms_news(bot, job):
    theresult = socialschoolcms.get_newsitems(settings)
    for user_id in settings.SEND_TO:
        for message in theresult:
            logger.info('News item to %d: %s', user_id, message)
            bot.send_message(chat_id=user_id, text=message)


def check_socialschoolcms_agenda(bot, update):
    theresult = socialschoolcms.get_agenda(settings)
    for user_id in settings.SEND_TO:
        for message in theresult:
            logger.info('Agenda message to %d: %s', user_id, message)
            bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)


def check_news_feeds(bot, update):
    theresult = feed.get_feedupdates(settings)
    for user_id in settings.SEND_TO:
        for message in theresult:
            logger.info('Newsfeed message to %d: %s', user_id, message['message'])
            bot.send_message(chat_id=user_id, text=message['message'], parse_mode=ParseMode.HTML)
            if message['images']:
                for image in message['images']:
                    logger.info('Newsfeed image to %d: %s', user_id, image)
                    bot.send_photo(chat_id=user_id, photo=image)


def check_trello(bot, update):
    theresult = trello.get_todays_planning(settings)
    return
    for recipient in theresult:
        if recipient != 'none':
            # Only send to specific user
            user_id = settings.TRELLO_INITIALS_TO_TELEGRAM[recipient]
            for message in theresult[recipient]:
                bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)
        else:
            for message in theresult[recipient]:
                for user_id in settings.SEND_TO:
                    bot.send_message(chat_id=user_id, text=message, parse_mode=ParseMode.HTML)


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it the bot's token.
    updater = Updater(settings.TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("reminder", set_reminder,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("remindall", set_remindall,
                                  pass_args=True,
                                  pass_job_queue=True,
                                  pass_chat_data=True))
    dp.add_handler(CommandHandler("unset", unset, pass_chat_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(InlineQueryHandler(inlinequery))
    dp.add_handler(MessageHandler(Filters.text, send_response))

    # log all errors
    dp.add_error_handler(error)

    # Enqueue updates
    if settings.SOCIALSCHOOLCMS_SCHOOL:
        # Sanity check
        if not settings.SEND_TO:
            logger.error('Please set user IDs in settings.py SEND_TO to send updates to')
            quit()
        dp.add_handler(CommandHandler("schoolagenda", check_socialschoolcms_agenda))

        j = updater.job_queue
        logger.info('Will check for SocialSchoolCMS')
        # Schedule repeating task, running every hour (3600 seconds)
        j.run_repeating(check_socialschoolcms_news, interval=3600, first=0)

    if settings.FEEDS:
        j = updater.job_queue
        logger.info('Will check for news feeds')
        # Schedule repeating task, running slightly more often than every hour
        j.run_repeating(check_news_feeds, interval=3540, first=0)

    if settings.TRELLO_APIKEY:
        j = updater.job_queue
        logger.info('Will check for Trello list items')
        # Schedule repeating task, running every day at 7 o'clock in the morning
        j.run_repeating(check_trello, interval=24*3600, first=datetime.time(7,0))

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
