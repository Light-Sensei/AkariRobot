import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from AkariRobot.events import register
from AkariRobot import telethn as tbot

PHOTO = "https://telegra.ph/file/7ef542475e2b5962144d1.mp4"

@register(pattern=("/premium"))
async def premium(event):
  TEXT = f"Yoooi [{event.sender.first_name}](tg://user?id={event.sender.id})-San \n\n"
  TEXT += "So You Want Premium Don't You\n\n"
  TEXT += f"Well You Can Learn More About Premium User Features [Here]()\n\n"
  TEXT += f"So Basically You Just Need To Add The Bot In % Groups For 1 Month Subscription\n\n"
  TEXT += f"20 Groups For 1 Year Subscription\n\n"
  TEXT += f"And Fiaanlly 50 Groups For Life Time\n\n"
  TEXT += "After You've Added Me In The Groups Contact @Yagami_Kun /n/n "
  BUTTON = [[Button.url("ᴀᴅᴅ ᴍᴇ", "t.me/AkariWatanabeXRoBot?startgroup=new"), Button.url("sᴜᴘᴘᴏʀᴛ", "https://t.me/shikimoriXsupport")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
