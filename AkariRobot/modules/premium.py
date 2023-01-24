import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from AkariRobot.events import register
from AkariRobot import telethn as tbot



@register(pattern=("/premium"))
async def premium(event):
  TEXT = f"Yoooi [{event.sender.first_name}](tg://user?id={event.sender.id})-San \n"
  TEXT += "Here's a Basic about premium \n"
  TEXT += f"┗━ Added Extra Features\n"
  TEXT += f"┗━ Automatic Approval In All Chats\n"
  TEXT += f"┗━ Resistive Towards /mute\n"
  TEXT += f"┗━ Can Request For Gban\n"
  TEXT += "For More Info Read [This](t.me/akariwatanabesupport\n\n\n"
  TEXT += "To Apply For Premium:\n"
  TEXT += "» 5 Groups = 1 Month Subscription\n"
  TEXT += "» 20 Groups = 1 Year Subscription\n"
  TEXT += "» 50 Groups = Life Time Subscription"
  BUTTON = [[Button.url("ᴀᴅᴅ ᴍᴇ", "t.me/AkariWatanabeXRoBot?startgroup=new"), Button.url("sᴜᴘᴘᴏʀᴛ", "https://t.me/shikimoriXsupport")]]
  await tbot.send_file(event.chat_id, caption=TEXT,  buttons=BUTTON)
