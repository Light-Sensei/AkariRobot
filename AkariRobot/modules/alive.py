import os
import re
from platform import python_version as kontol
from telethon import events, Button
from telegram import __version__ as telever
from telethon import __version__ as tlhver
from pyrogram import __version__ as pyrover
from AkariRobot.events import register
from AkariRobot import telethn as tbot


PHOTO = "https://telegra.ph/file/bd9ce6e2c66833236248d.mp4"

@register(pattern=("/alive"))
async def awake(event):
  TEXT = f"やあ Kon'ichiwa [{event.sender.first_name}](tg://user?id={event.sender.id})-San, Watashi Wa Shikimori Des. \n\n"
  TEXT += "♡ Am Functioning Properly Duh ♡ \n\n"
  TEXT += f"♡ My Darling : [Light Yagami♡ (夜神月♡)](t.me/yagami_roito)** \n\n"
  TEXT += f"♡ Library Version : `{telever}` \n"
  TEXT += f"♡ Telethon Version : `{tlhver}` \n"
  TEXT += f"♡ Pyrogram Version : `{pyrover}` \n"
  TEXT += "♡ Arigato For Adding me Here ♡"
  BUTTON = [[Button.url("ᴜᴘᴅᴀᴛᴇs", "https://t.me/ShikimoriXupdates"), Button.url("sᴜᴘᴘᴏʀᴛ", "https://t.me/shikimoriXsupport")]]
  await tbot.send_file(event.chat_id, PHOTO, caption=TEXT,  buttons=BUTTON)
