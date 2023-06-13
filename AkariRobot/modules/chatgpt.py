import json
import re
import os
import html
import openai
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
from AkariRobot import dispatcher, updater, SUPPORT_CHAT
from AkariRobot.modules.log_channel import gloggable


# Configure the logging module
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Define your bot token here
TOKEN = 'YOUR_BOT_TOKEN'

# Command handlers
def gpt(update, context):
    """Handler for the /gpt command"""
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm akari robot.")

def gptecho(update, context):
    """Handler for echoing user messages"""
    message = update.message
    context.bot.send_message(chat_id=message.chat_id, text=message.text)

def time(update, context):
    """Handler for the /time command"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    context.bot.send_message(chat_id=update.effective_chat.id, text=f"Current time: {current_time}")

def errorgpt(update, context):
    """Handler for handling errors"""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    
    
 __help__ = """
Chatgpt utilizes the Kuki's api which allows Kuki to talk and provide a more interactive group chat experience.
*Admins only Commands*:
  ➢ `/startgpt`*:* Shows chatbot control panel
*Powered by ItelAi*
"""

__mod_name__ = "ChatBot"


GPT_HANDLER = CommandHandler("gpt", gpt, run_async=True)
TIME_HANDLER = CommandHandler("time", time, run_async=True)
GPTECHO_HANDLER = CommandHandler("gptecho", gptecho, run_async=True)
ERRORGPT_HANDLER = ErrorHandler("errorgpt", errorgpt, runasync=True)

dispatcher.add_handler(GPT_HANDLER)
dispatcher.add_handler(TIME_HANDLER)
dispatcher.add_handler(GPTECHO_HANDLER)
dispatcher.add_handler(ERRORGPT_HANDLER)

__handlers__ = [
    GPT_HANDLER,
    TIME_HANDLER,
    GPTECHO_HANDLER,
    ERRORGPT_HANDLER,
]
    
