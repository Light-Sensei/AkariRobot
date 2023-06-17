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
from pymongo import MongoClient
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode, Update, Message
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.utils.helpers import mention_html

from AkariRobot import OWNER_ID, REDIS, dispatcher
from AkariRobot.modules.disable import DisableAbleCommandHandler
from AkariRobot.modules.helper_funcs.alternate import typing_action
from AkariRobot.modules.helper_funcs.chat_status import callbacks_in_filters



MONGO_DB_URI = os.getenv("MONGO_DB_URI")
if not MONGO_DB_URI:
    raise ValueError("MongoDB URI is not set")

# Connect to MongoDB server
client = MongoClient(MONGO_DB_URI)

# Select the database and collection
db = client['your_database']
collection = db['your_collection']


def playrpg(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    # Check if the user is already registered
    if collection.count_documents({'_id': user_id}) > 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are already playing the RPG!")
        return

    mention = mention_html(user_id, update.effective_user.first_name)
    start_message = (
        f"Hey {mention}! Welcome to our virtual world.\n\n"
        "Are you ready to face all the upcoming challenges?\n"
        "If yes, choose /create to start playing."
    )
    context.bot.send_message(chat_id=update.effective_chat.id, text=start_message, parse_mode=ParseMode.HTML)


def create(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    # Check if the user is already registered
    if collection.count_documents({'_id': user_id}) > 0:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have already created a character!")
        return

    gender_keyboard = [
        [InlineKeyboardButton("Male", callback_data='male')],
        [InlineKeyboardButton("Female", callback_data='female')]
    ]
    reply_markup = InlineKeyboardMarkup(gender_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ok, so what is your gender?", reply_markup=reply_markup)


# Callback handler for gender selection
def select_gender(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = str(query.from_user.id)
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
    user_id = str(query.from_user.id)
    name = query.data
    query.answer()

    # Insert character details into the database
    data = {
        '_id': user_id,
        'name': name,
        'balance': 0  # Initialize balance to 0
    }
    collection.insert_one(data)

    query.message.edit_text(f"Okay, {name}! Let's enter this beautiful realm of magic.")


def get_player_data(user_id):
    player_data = collection.find_one({'user_id': user_id})
    if not player_data:
        player_data = {'user_id': user_id, 'balance': 0, 'inventory': [], 'bank_balance': 0, 'last_daily': None, 'last_weekly': None}
        collection.insert_one(player_data)
    return player_data

# Function to update the player's data in the database
def update_player_data(user_id, player_data):
    collection.update_one({'user_id': user_id}, {'$set': player_data})

# Function to handle the /bal command
def balance(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)
    real_balance = player_data['balance']
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your balance: {real_balance} coins.")

# Function to handle the /daily command
def daily(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)
    last_daily = player_data['last_daily']
    if last_daily is not None:
        time_diff = datetime.now() - last_daily
        if time_diff.days < 1:
            context.bot.send_message(chat_id=update.effective_chat.id, text="You have already claimed your daily reward. Try again tomorrow!")
            return

    balance = player_data['balance']
    new_balance = balance + 50  # Increment balance by 50 for daily reward
    player_data['balance'] = new_balance
    player_data['last_daily'] = datetime.now()
    update_player_data(user_id, player_data)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You received a daily reward of 50 coins. Your balance is now {new_balance} coins.")

# Function to handle the /weekly command
def weekly(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)
    last_weekly = player_data['last_weekly']
    if last_weekly is not None:
        time_diff = datetime.now() - last_weekly
        if time_diff.days < 7:
            remaining_days = 7 - time_diff.days
            context.bot.send_message(chat_id=update.effective_chat.id, text=f"You have already claimed your weekly reward. Try again after {remaining_days} days!")
            return

    balance = player_data['balance']
    new_balance = balance + 100  # Increment balance by 100 for weekly reward
    player_data['balance'] = new_balance
    player_data['last_weekly'] = datetime.now()
    update_player_data(user_id, player_data

# Function to handle the /inv command
def inventory(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)
    balance = player_data['balance']
    inventory_items = player_data['inventory']
    inventory_text = f"Your inventory:\nBalance: {balance} coins\nItems: {', '.join(inventory_items)}"
    context.bot.send_message(chat_id=update.effective_chat.id, text=inventory_text)

# Function to handle the /hunt command
def hunt(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)
    balance = player_data['balance']
    earnings = random.randint(1, 10)  # Random earnings between 1 and 10
    new_balance = balance + earnings
    player_data['balance'] = new_balance
    update_player_data(user_id, player_data)
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You went hunting and earned {earnings} coins. Your balance is now {new_balance} coins.")

# Function to handle the /build command
def build(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)
    balance = player_data['balance']
    cost = 50  # Cost to build
    if balance >= cost:
        new_balance = balance - cost
        player_data['balance'] = new_balance
        # Add the built item to the inventory
        built_item = "Sword"  # Replace with the item you want to build
        player_data['inventory'].append(built_item)
        update_player_data(user_id, player_data)
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You built a {built_item} for {cost} coins. Your balance is now {new_balance} coins.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have enough coins to build.")

def deposit(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)

    if player_data['balance'] > 0:
        player_data['bank_balance'] += player_data['balance']
        player_data['balance'] = 0

        # Update the player data in the database
        update_player_data(user_id, player_data)

        context.bot.send_message(chat_id=update.effective_chat.id, text="You have deposited all your coins to the bank.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You don't have any coins to deposit.")

# Function to handle the /withdraw command
def withdraw(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)

    if player_data['bank_balance'] > 0:
        player_data['balance'] += player_data['bank_balance']
        player_data['bank_balance'] = 0

        # Update the player data in the database
        update_player_data(user_id, player_data)

        context.bot.send_message(chat_id=update.effective_chat.id, text="You have withdrawn all your coins from the bank.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Your bank balance is empty.")

# Function to handle the /bank command
def bank(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)

    bank_balance = player_data['bank_balance']
    balance = player_data['balance']

    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Bank balance: {bank_balance} coins\nWallet balance: {balance} coins")





playrpg_handler = CommandHandler("playrpg", playrpg, run_async=True)
create_handler = CommandHandler("create", create, run_async=True)
weekly_handler = CommandHandler("weekly", weekly, run_async=True)
inventory_handler = CommandHandler("inv", inventory, run_async=True)
hunt_handler = CommandHandler("hunt", hunt, run_async=True)
build_handler = CommandHandler("build", build, run_async=True)
bank_handler = CommandHandler("bank", bank, run_async=True)
deposit_handler = CommandHandler("deposit", deposit, run_async=True)
withdraw_handler = CommandHandler("withdraw", withdraw, run_async=True)
daily_handler = CommandHandler("daily", daily, run_async=True)
balance_handler = CommandHandler("bal", balance, run_async=True)


gender_callback_handler = CallbackQueryHandler(select_gender, pattern='^(male|female)$', run_async=True)
name_callback_handler = CallbackQueryHandler(select_name, pattern='^(Jake|Zade|Josh|Aaron|Atlas|Mike|Jane|Lily|Julliete|Adeline|Grace|Olivia)$', run_async=True)



dispatcher.add_handler(weekly_handler)
dispatcher.add_handler(inventory_handler)
dispatcher.add_handler(hunt_handler)
dispatcher.add_handler(build_handler)
dispatcher.add_handler(bank_handler)
dispatcher.add_handler(deposit_handler)
dispatcher.add_handler(withdraw_handler)
dispatcher.add_handler(playrpg_handler)
dispatcher.add_handler(create_handler)
dispatcher.add_handler(gender_callback_handler)
dispatcher.add_handler(name_callback_handler)
dispatcher.add_handler(daily_handler)
dispatcher.add_handler(balance_handler)


__mod_name__ = "RPG"
__command_list__ = [
    "playrpg",
    "create",
]
__handlers__ = [
    create_handler,
    daily_handler,
    weekly_handler,
    balance_handler,
    withdraw_handler,
    deposit_handler,
    bank_handler,
    build_handler,
    inventory_handler,
    playrpg_handler,
    hunt_handler,
    gender_callback_handler,
    name_callback_handler,
] 





