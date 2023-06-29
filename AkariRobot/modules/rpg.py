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
def weekly(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)

    if player_data['weekly_claimed']:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have already claimed your weekly reward.")
    else:
        reward = random.choice(['sword', 'coins', 'steel'])
        if reward == 'sword':
            player_data['inventory'].append('sword')
            context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations! You received a high-quality sword.")
        elif reward == 'coins':
            player_data['balance'] += 500
            context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations! You received 500 coins.")
        elif reward == 'steel':
            player_data['inventory'].append('steel')
            context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations! You received some steel.")

        player_data['weekly_claimed'] = True
        update_player_data(user_id, player_data)

# Function to handle the /daily command
def daily(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    player_data = get_player_data(user_id)

    last_claimed = player_data.get('last_daily_claimed')
    if last_claimed and datetime.datetime.now() - last_claimed < datetime.timedelta(days=1):
        context.bot.send_message(chat_id=update.effective_chat.id, text="You have already claimed your daily reward.")
    else:
        player_data['balance'] += 100
        player_data['last_daily_claimed'] = datetime.datetime.now()
        update_player_data(user_id, player_data)

        context.bot.send_message(chat_id=update.effective_chat.id, text="Congratulations! You received 100 coins.")


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
    build_keyboard = [
        [InlineKeyboardButton("Sword", callback_data='build_sword')],
        [InlineKeyboardButton("Shield", callback_data='build_shield')],
        [InlineKeyboardButton("House", callback_data='build_house')],
        [InlineKeyboardButton("Farm", callback_data='build_farm')],
        [InlineKeyboardButton("Garden", callback_data='build_garden')],
        [InlineKeyboardButton("Storage", callback_data='build_storage')],
        [InlineKeyboardButton("Fortress", callback_data='build_fortress')],
        [InlineKeyboardButton("Castle", callback_data='build_castle')],
        [InlineKeyboardButton("Minarets", callback_data='build_minarets')],
        [InlineKeyboardButton("Towers", callback_data='build_towers')],
    ]
    
    reply_markup = InlineKeyboardMarkup(build_keyboard)
    update.message.reply_text("Select an item to build:", reply_markup=reply_markup)

# Callback handler for build item selection
def select_build_item(update: Update, context: CallbackContext):
    query = update.callback_query
    item = query.data.replace("build_", "")
    query.answer()
    
    user_id = str(query.from_user.id)
    player_info = player_data.get(user_id, {})
    
    if item in ["sword", "shield", "house", "farm", "garden", "storage", "fortress", "castle", "minarets", "towers"]:
        player_info['built_items'] = player_info.get('built_items', {})
        player_info['built_items'][item] = player_info['built_items'].get(item, 0) + 1
        player_data[user_id] = player_info
        query.edit_message_text(f"You have successfully built a {item}!")
    else:
        query.edit_message_text("Invalid build item.")

# Base Command
def base(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    player_info = player_data.get(user_id, {})
    built_items = player_info.get('built_items', {})
    
    base_message = "Your base:\n\n"
    for item, count in built_items.items():
        base_message += f"{item.capitalize()}: {count}\n"
    
    update.message.reply_text(base_message)

# Create Kingdom Command
def create_kingdom(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    player_info = player_data.get(user_id, {})
    built_items = player_info.get('built_items', {})
    
    minarets_count = built_items.get('minarets', 0)
    fortress_count = built_items.get('fortress', 0)
    castle_count = built_items.get('castle', 0)
    house_count = built_items.get('house', 0)
    storage_count = built_items.get('storage', 0)
    farm_count = built_items.get('farm', 0)
    garden_count = built_items.get('garden', 0)
    
    if minarets_count >= 10 and fortress_count >= 1 and castle_count >= 1 and house_count >= 20 and storage_count >= 1 and farm_count >= 5 and garden_count >= 10:
        player_info['kingdom'] = True
        player_data[user_id] = player_info
        update.message.reply_text("Congratulations! You have created a kingdom!")
    else:
        update.message.reply_text("You don't have enough built items to create a kingdom.")

# Upgrade Kingdom Command
def upgrade_kingdom(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)
    player_info = player_data.get(user_id, {})
    kingdom = player_info.get('kingdom', False)
    
    if kingdom:
        # Upgrade the kingdom logic
        # Add your upgrade logic here
        update.message.reply_text("Your kingdom has been upgraded!")
    else:
        update.message.reply_text("You don't have a kingdom to upgrade.")


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
bank_handler = CommandHandler("bank", bank, run_async=True)
deposit_handler = CommandHandler("deposit", deposit, run_async=True)
withdraw_handler = CommandHandler("withdraw", withdraw, run_async=True)
daily_handler = CommandHandler("daily", daily, run_async=True)
balance_handler = CommandHandler("bal", balance, run_async=True)
BUILD_HANDLER = CommandHandler("build", build)
BASE_HANDLER = CommandHandler("base", base)
CREATE_KINGDOM_HANDLER = CommandHandler("create_kingdom", create_kingdom)
UPGRADE_KINGDOM_HANDLER = CommandHandler("upgrade_kingdom", upgrade_kingdom)


gender_callback_handler = CallbackQueryHandler(select_gender, pattern='^(male|female)$', run_async=True)
name_callback_handler = CallbackQueryHandler(select_name, pattern='^(Jake|Zade|Josh|Aaron|Atlas|Mike|Jane|Lily|Julliete|Adeline|Grace|Olivia)$', run_async=True)



dispatcher.add_handler(weekly_handler)
dispatcher.add_handler(inventory_handler)
dispatcher.add_handler(hunt_handler)
dispatcher.add_handler(bank_handler)
dispatcher.add_handler(deposit_handler)
dispatcher.add_handler(withdraw_handler)
dispatcher.add_handler(playrpg_handler)
dispatcher.add_handler(create_handler)
dispatcher.add_handler(gender_callback_handler)
dispatcher.add_handler(name_callback_handler)
dispatcher.add_handler(daily_handler)
dispatcher.add_handler(balance_handler)
dispatcher.add_handler(BUILD_HANDLER)
dispatcher.add_handler(BASE_HANDLER)
dispatcher.add_handler(CREATE_KINGDOM_HANDLER)
dispatcher.add_handler(UPGRADE_KINGDOM_HANDLER)

__mod_name__ = "RPG"
__command_list__ = [
    "playrpg",
    "create",
]
__handlers__ = [
    create_handler,
    daily_handler,
    select_build_item,
    weekly_handler,
    balance_handler,
    withdraw_handler,
    deposit_handler,
    bank_handler,
    inventory_handler,
    playrpg_handler,
    hunt_handler,
    gender_callback_handler,
    name_callback_handler,
] 




