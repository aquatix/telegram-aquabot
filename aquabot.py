#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Simple Bot to reply to Telegram messages, set timers and provide updates.

This program is dedicated to the public domain under the CC0 license.

This Bot uses the Updater class to handle the bot.

First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Give periodic updates from various sources. Set alarm message with timer.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import re
from uuid import uuid4

from telegram import (InlineQueryResultArticle, InputTextMessageContent,
                      ParseMode)
from telegram.ext import (CommandHandler, Filters, InlineQueryHandler,
                          MessageHandler, Updater)
from telegram.utils.helpers import escape_markdown

from plugins import socialschoolcms
import settings

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
    update.message.reply_text('You can type \'school\' to get updates, or set a timer with /set <seconds>')


def alarm(bot, job):
    """Send the alarm message."""
    bot.send_message(job.context, text='Beep!')


def set_timer(bot, update, args, job_queue, chat_data):
    """Add a job to the queue."""
    chat_id = update.message.chat_id
    try:
        # args[0] should contain the time for the timer in seconds
        due = int(args[0])
        if due < 0:
            update.message.reply_text('Sorry we can not go back to future!')
            return

        # Add job to queue
        job = job_queue.run_once(alarm, due, context=chat_id)
        chat_data['job'] = job

        update.message.reply_text('Timer successfully set!')

    except (IndexError, ValueError):
        update.message.reply_text('Usage: /set <seconds>')


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


def check_socialschoolcms(bot, job):
    theresult = socialschoolcms.get_newsitems(settings)
    for user_id in settings.SEND_TO:
        for message in theresult:
            bot.send_message(chat_id=user_id, text=message)


def check_socialschoolcms_agenda(bot, update):
    theresult = socialschoolcms.get_agenda(settings)
    for message in theresult:
        bot.send_message(chat_id=update.message.chat_id, text=message, parse_mode=ParseMode.HTML)


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
    dp.add_handler(CommandHandler("set", set_timer,
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
        dp.add_handler(CommandHandler("schoolagenda", check_socialschoolcms_agenda))

        j = updater.job_queue
        print('Will check for SocialSchoolCMS')
        j.run_repeating(check_socialschoolcms, interval=3600, first=0)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
