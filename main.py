#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Initial bot framework taken from Andrés Ignacio Torres <andresitorresm@gmail.com>
"""

import os, logging
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from urllib.error import HTTPError
from dotenv import load_dotenv
from inspect import cleandoc
load_dotenv('./.env')

class DiscordBot:
    """
    A class to encapsulate all relevant methods of the bot.
    """

    def __init__(self):
        """
        Constructor of the class. Initializes certain instance variables
        and checks if everything's O.K. for the bot to work as expected.
        """

        # This environment variable should be set before using the bot
        self.token = os.environ['TELEGRAM_BOT_TOKEN']

        # These will be checked against as substrings within each
        # message, so different variations are not required if their
        # radix is present (e.g. "all" covers "/all" and "ball")
        self.menu_trigger = ['/menu']

        # Stops runtime if no bot token has been set
        if self.token is None:
            raise RuntimeError(
                "FATAL: No token was found. " + \
                "You might need to specify one or more environment variables.")

        # Configures logging in debug level to check for errors
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.DEBUG)


    def run_bot(self):
        """
        Sets up the required bot handlers and starts the polling
        thread in order to successfully reply to messages.
        """

        # Instantiates the bot updater
        self.updater = Updater(self.token, use_context=True)
        self.dispatcher = self.updater.dispatcher

        # Declares and adds handlers for commands that shows help info
        start_handler = CommandHandler('start', self.start_dialogue)
        help_handler = CommandHandler('help', self.show_menu)
        self.dispatcher.add_handler(start_handler)
        self.dispatcher.add_handler(help_handler)

        # Declares and adds a handler for text messages that will reply with
        # a response if the message includes a trigger word
        text_handler = MessageHandler(Filters.text, self.handle_text_messages)
        self.dispatcher.add_handler(text_handler)

        # Fires up the polling thread. We're live!
        self.updater.start_polling()


    def parse_msg(self, msg):
        """
        Helper function to make text output compatible with telegram
        and remove weird indentation from multiline strings
        """
        escape_d = {
            '.': '\.',
            '!': '\!',
            '(': '\(',
            ')': '\)',
            '-': '\-',
            }
        return cleandoc(msg.translate(msg.maketrans(escape_d)))


    def show_menu(self, update, context):
        """
        Shows the menu with current items.
        """

        MENU_MSG = "*Bot Commands*\n\n" + \
                    "/add a Discord channel\n" + \
                    "/edit Discord channels\n" + \
                    "/edit Discord handle"

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=MENU_MSG,
            parse_mode='MarkdownV2'
            )


    def start_dialogue(self, update, context):
        """
        Initiates the dialogue that appears when the bot is called by a user
        for the first time.
        """

        welcome_msg = self.parse_msg(
        """
        Welcome!
        This bot notifies you if your discord handle has been mentioned in a
        selection of Discord channels of your choosing.
        You can always get to the bot menu by typing /menu.
        """
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=welcome_msg,
            parse_mode='MarkdownV2'
            )

        self.add_channel(update, context)


    def add_channel(self, update, context):

        add_channel_msg = self.parse_msg(
        """
        Please type in a Discord channel address you want to receive notifications for,
        i.e. https://discord.gg/bh34Btvy or
        https://discord.com/channels/8276553372938765120/009266357485627752.

        You can get this information if you press and hold the Discord channel (mobile),
        select 'Invite', then 'Copy link', or right-click on the channel (laptop) and
        click 'Copy Link'.
        """
        )

        context.bot.send_message(
            chat_id=update.message.chat_id,
            text=add_channel_msg,
            disable_web_page_preview=True,
            parse_mode='MarkdownV2'
            )


    def handle_text_messages(self, update, context):
        """
        Checks if a message comes from a group. If that is not the case,
        or if the message includes a trigger word, replies with merch.
        """
        words = set(update.message.text.lower().split())
        logging.debug(f'Received message: {update.message.text}')
        logging.debug(f'Splitted words: {", ".join(words)}')

        # For debugging: Log users that recieved message from bot
        chat_user_client = update.message.from_user.username
        if chat_user_client == None:
            chat_user_client = update.message.chat_id
            logging.info(f'{chat_user_client} interacted with the bot.')

        # Possibility: received command from menu_trigger
        for Trigger in self.menu_trigger:
            for word in words:
                if word.startswith(Trigger):
                    self.show_menu(update, context)
                    return

        # Possibility: received command from text_trigger
        for Trigger in self.text_trigger:
            for word in words:
                if word.startswith(Trigger):
                    file = self.message_map[Trigger]
                    self.send_text(file, update, context)
                    self.send_signature(update, context)
                    print(f'{chat_user_client} got links!')
                    return


def main():
    """
    Entry point of the script. If run directly, instantiates the
    DiscordBot class and fires it up.
    """

    discord_bot = DiscordBot()
    discord_bot.run_bot()


# If the script is run directly, fires the main procedure
if __name__ == "__main__":
    main()


# TODO: Switch off logging before bot is 'released'
