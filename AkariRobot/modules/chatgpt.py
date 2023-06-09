import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import openai
import json
import re
import os
import html
import requests
import AkariRobot.modules.sql.chatbot_sql as sql

from time import sleep
from telegram import ParseMode
from telegram import (CallbackQuery, Chat, MessageEntity, InlineKeyboardButton,
                      InlineKeyboardMarkup, Message, ParseMode, Update, Bot, User)
from telegram.ext import (CallbackContext, CallbackQueryHandler, CommandHandler,
                          DispatcherHandlerStop, Filters, MessageHandler,
                          run_async)
from telegram.error import BadRequest, RetryAfter, Unauthorized
from telegram.utils.helpers import mention_html, mention_markdown, escape_markdown

from AkariRobot.modules.helper_funcs.filters import CustomFilters
from AkariRobot.modules.helper_funcs.chat_status import user_admin, user_admin_no_reply
from AkariRobot import dispatcher, updater, SUPPORT_CHAT, TOKEN, OPEN_API_KEY
from AkariRobot.modules.log_channel import gloggable

@run_async
@user_admin_no_reply
@gloggable

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Define a function to handle /chatgpt command
def chatgpt(update: Update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a Akari's Chatgpt. How can I assist you?")

# Define a function to handle incoming messages
def message_handler(update: Update, context):
    # Get the user's message
    user_message = update.message.text
    
    # Call the ChatGPT model
    response = chat_with_gpt(user_message)
    
    # Send the response back to the user
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)

# Function to interact with ChatGPT
def chat_with_gpt(user_message):
    # Call OpenAI API to get a response
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=user_message,
        max_tokens=50,
        temperature=0.7,
        n=1,
        stop=None,
        context=None,
        log_level=None,
    )
    
    # Extract and return the response
    return response.choices[0].text

# Set up the Telegram bot
def main():
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Define the command handlers
    chatgpt_handler = CommandHandler('chatgpt', chatgpt)
    dispatcher.add_handler(chatgpt_handler)

    # Define the message handler
    message_handler = MessageHandler(Filters.text & ~Filters.command, message_handler)
    dispatcher.add_handler(message_handler)

    # Start the bot
    updater.start_polling()
    updater.idle()

__mod_name__ = "CHATGPT"
__command_list__ = ["chatgpt"]
