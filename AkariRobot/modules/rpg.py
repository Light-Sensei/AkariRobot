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
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, Message
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.utils.helpers import mention_html

from AkariRobot import OWNER_ID, REDIS, dispatcher
from AkariRobot.modules.disable import DisableAbleCommandHandler
from AkariRobot.modules.helper_funcs.alternate import typing_action
from AkariRobot.modules.helper_funcs.chat_status import callbacks_in_filters



def playrpg(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome to the RPG bot! Use /create to start playing.")

def create(update, context):
    keyboard = [
        [InlineKeyboardButton("Male", callback_data='male')],
        [InlineKeyboardButton("Female", callback_data='female')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Choose your gender:", reply_markup=reply_markup)

def create_character(update, context):
    query = update.callback_query
    gender = query.data
    query.answer()
    context.bot.send_message(chat_id=query.message.chat_id, text=f"You selected: {gender}")   

def daily(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You received your daily reward!")

def weekly(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="You received your weekly reward!")

def balance(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Your current balance is: $100")

def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    playrpg_handler = CommandHandler('playrpg', playrpg)
    create_handler = CommandHandler('create', create)
    create_character_handler = CallbackQueryHandler(create_character)
    daily_handler = CommandHandler('daily', daily)
    weekly_handler = CommandHandler('weekly', weekly)
    balance_handler = CommandHandler('balance', balance)

    dispatcher.add_handler(playrpg_handler
    dispatcher.add_handler(create_handler)
    dispatcher.add_handler(create_character_handler)
    dispatcher.add_handler(daily_handler)
    dispatcher.add_handler(weekly_handler)
    dispatcher.add_handler(balance_handler)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
