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


def daily(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    # Retrieve the user's data from the database
    data = collection.find_one({'_id': user_id})
    if data:
        balance = data.get('balance')
        new_balance = balance + 10  # Daily bonus of 10 gold coins
        collection.update_one({'_id': user_id}, {'$set': {'balance': new_balance}})

        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You earned 10 gold coins. Your balance: {new_balance}")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not registered. Use /create to create a character.")


def balance(update: Update, context: CallbackContext):
    user_id = str(update.effective_user.id)

    # Retrieve the user's balance from the database
    data = collection.find_one({'_id': user_id})
    if data:
        balance = data.get('balance')
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your balance: {balance} gold coins")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="You are not registered. Use /create to create a character.")




# Command handler for /weekly
def weekly(update: Update, context: CallbackContext):
    # Generate a random reward for the weekly command
    rewards = ["500 gold coins", "lucky item tap /spin to see", "a treasure map"]
    reward = random.choice(rewards)
    
    # Send the reward to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"You received {reward} as your weekly reward!")



# Command handler for /inv
def inventory(update: Update, context: CallbackContext):
    # Get the user's inventory from the database or any other storage
    items = ["Sword", "Shield", "Health Potion"]  # Replace with the actual inventory retrieval code
    
    # Format the items into a list
    items_list = "\n".join(items)
    
    # Send the user's inventory to the chat
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Your inventory:\n{items_list}")

# Command handler for /hunt
def hunt(update: Update, context: CallbackContext):
    # Generate a random number to simulate the success of hunting
    success = random.randint(0, 1)
    
    if success:
        # User successfully hunted an animal
        animal = random.choice(["rabbit", "deer", "wolf"])
        context.bot.send_message(chat_id=update.effective_chat.id, text=f"You hunted a {animal}!")
    else:
        # User failed to hunt an animal and got injured
        context.bot.send_message(chat_id=update.effective_chat.id, text="While hunting, you got injured. Try again later.")

# Command handler for /build
def build(update: Update, context: CallbackContext):
    # Generate a random number to simulate the success of building
    success = random.randint(0, 1)
    
    if success:
        # User successfully built something
        context.bot.send_message(chat_id=update.effective_chat.id, text="You successfully built a house!")
    else:
        # User failed to build something
        context.bot.send_message(chat_id=update.effective_chat.id, text="Building construction failed. Try again later.")

# Define command handlers


# Add handlers to the dispatcher




playrpg_handler = CommandHandler("playrpg", playrpg, run_async=True)
create_handler = CommandHandler("create", create, run_async=True)
daily_handler = CommandHandler("daily", daily, run_async=True)
weekly_handler = CommandHandler("weekly", weekly, run_async=True)
balance_handler = CommandHandler("bal", balance, run_async=True)
inventory_handler = CommandHandler("inv", inventory, run_async=True)
hunt_handler = CommandHandler("hunt", hunt, run_async=True)
build_handler = CommandHandler("build", build, run_async=True)

gender_callback_handler = CallbackQueryHandler(select_gender, pattern='^(male|female)$', run_async=True)
name_callback_handler = CallbackQueryHandler(select_name, pattern='^(Jake|Zade|Josh|Aaron|Atlas|Mike|Jane|Lily|Julliete|Adeline|Grace|Olivia)$', run_async=True)

# Add handlers to the dispatcher
dispatcher.add_handler(playrpg_handler)
dispatcher.add_handler(create_handler)
dispatcher.add_handler(gender_callback_handler)
dispatcher.add_handler(name_callback_handler)
dispatcher.add_handler(daily_handler)
dispatcher.add_handler(weekly_handler)
dispatcher.add_handler(balance_handler)
dispatcher.add_handler(inventory_handler)
dispatcher.add_handler(hunt_handler)
dispatcher.add_handler(build_handler)

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
    build_handler,
    inventory_handler,
    playrpg_handler,
    hunt_handler,
    gender_callback_handler,
    name_callback_handler,
] 






