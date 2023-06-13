import datetime
import html
import json
import textwrap
import bs4
import jikanpy
import requests
import random
import os

from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, Message
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.utils.helpers import mention_html

from AkariRobot import OWNER_ID, REDIS, dispatcher
from AkariRobot.modules.disable import DisableAbleCommandHandler
from AkariRobot.modules.helper_funcs.alternate import typing_action
from AkariRobot.modules.helper_funcs.chat_status import callbacks_in_filters



def playrpg(update: Update, context: CallbackContext):
    user = update.effective_user
    mention = mention_html(user.id, user.first_name)
    start_message = (
        f"hey {mention}! Welcome to the our virtual world.\n\n"
        "are you ready to face all the upcoming challenges?\n"
        "if yes then choose /create to start playing."
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_message, parse_mode=ParseMode.HTML)
    


def create(update: Update, context: CallbackContext):
    gender_keyboard = [
        [InlineKeyboardButton("Male", callback_data='male')],
        [InlineKeyboardButton("Female", callback_data='female')]
    ]
    reply_markup = InlineKeyboardMarkup(gender_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ok, so what is your gender?", reply_markup=reply_markup)

# Callback handler for gender selection
def select_gender(update: Update, context: CallbackContext):
    query = update.callback_query
    gender = query.data
    query.answer()

    if gender == 'male':
        name_keyboard = [
            [
                InlineKeyboardButton("Jake", callback_data='Jake'),
                InlineKeyboardButton("Zade", callback_data='Zade'),
                InlineKeyboardButton("Josh", callback_data='Josh'),
            ],
            [
                InlineKeyboardButton("Aaron", callback_data='Aaron'),
                InlineKeyboardButton("Atlas", callback_data='Atlas'),
                InlineKeyboardButton("Mike", callback_data='Mike'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(name_keyboard)
        query.message.reply_text("Alright, you're a male. Choose your name:", reply_markup=reply_markup)
    elif gender == 'female':
        name_keyboard = [
            [
                InlineKeyboardButton("Jane", callback_data='Jane'),
                InlineKeyboardButton("Lily", callback_data='Lily'),
                InlineKeyboardButton("Julliete", callback_data='Julliete')
            ],
            [
                InlineKeyboardButton("Adeline", callback_data='Adeline'),
                InlineKeyboardButton("Grace", callback_data='Grace'),
                InlineKeyboardButton("Olivia", callback_data='Olivia'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(name_keyboard)
        query.message.reply_text("Alright, you're a female. Choose your name:", reply_markup=reply_markup)

# Callback handler for character name selection
def select_name(update: Update, context: CallbackContext):
    query = update.callback_query
    name = query.data
    query.answer()
    query.message.edit_text(f"Okay, {name}! Let's enter this beautiful realm of magic.")

# Add callback handlers for each character name
name_callbacks = [
    CallbackQueryHandler(select_name, pattern='Jake'),
    CallbackQueryHandler(select_name, pattern='Zade'),
    CallbackQueryHandler(select_name, pattern='Josh'),
    CallbackQueryHandler(select_name, pattern='Aaron'),
    CallbackQueryHandler(select_name, pattern='Atlas'),
    CallbackQueryHandler(select_name, pattern='Mike'),
    CallbackQueryHandler(select_name, pattern='Jane'),
    CallbackQueryHandler(select_name, pattern='Lily'),
    CallbackQueryHandler(select_name, pattern='Julliete'),
    CallbackQueryHandler(select_name, pattern='Adeline'),
    CallbackQueryHandler(select_name, pattern='Grace'),
    CallbackQueryHandler(select_name, pattern='Olivia'),
]



PLAYRPG_HANDLER = CommandHandler("playrpg", playrpg, run_async=True)
BUTTON_HANDLER = CommandHandler("create", create, run_async=True)


dispatcher.add_handler(BUTTON_HANDLER)
dispatcher.add_handler(PLAYRPG_HANDLER)

for callback in name_callbacks:
    dispatcher.add_handler(NAME_CALLBACK)

__mod_name__ = "RPG"
__command_list__ = [
    "playrpg",
    "create",
]
__handlers__ = [
    BUTTON_HANDLER,
    PLAYRPG_HANDLER,
] + NAME_CALLBACKS





