# Daisyxmusic (Telegram bot project )
# Copyright (C) 2021  Inukaasith

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message, Chat, CallbackQuery
from EXmusic.config import SOURCE_CODE,ASSISTANT_NAME,PROJECT_NAME,SUPPORT_GROUP,UPDATES_CHANNEL,BOT_USERNAME, OWNER, BOT_NAME
logging.basicConfig(level=logging.INFO)
from EXmusic.helpers.filters import command
from time import time
from datetime import datetime
from EXmusic.helpers.decorators import authorized_users_only


START_TIME = datetime.utcnow()
START_TIME_ISO = START_TIME.replace(microsecond=0).isoformat()
TIME_DURATION_UNITS = (
    ('week', 60 * 60 * 24 * 7),
    ('day', 60 * 60 * 24),
    ('hour', 60 * 60),
    ('min', 60),
    ('sec', 1)
)

async def _human_time_duration(seconds):
    if seconds == 0:
        return 'inf'
    parts = []
    for unit, div in TIME_DURATION_UNITS:
        amount, seconds = divmod(int(seconds), div)
        if amount > 0:
            parts.append('{} {}{}'
                         .format(amount, unit, "" if amount == 1 else "s"))
    return ', '.join(parts)


@Client.on_message(
    filters.command(["help", f"help@{BOT_USERNAME}"])
    & filters.group
    & ~ filters.edited
)
async def help(client: Client, message: Message):
    await message.reply_text(
        f"""👋 Hello {message.from_user.mention()} **Please** press the button below to read the **explanation** and see the list of available **Commands**\n\nOr you can directly **contact** the creator if you need **help**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "💡 How to use bots ❔", callback_data=f"cbguide"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🧑‍💻 Creator", url=f"https://t.me/rizexx"
                    )
                ]
            ]
        ),
    ) 

@Client.on_message(
    filters.command("reload")
    & filters.group
    & ~ filters.edited
)
async def reload(client: Client, message: Message):
    await message.reply_text("""✅ Bots **Successful restart!**\n\n✅ **Admin list** Has been successfully **updated**""",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Group Support 🏷️", url=f"https://t.me/EXGroupSupport"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "Channel Update 📣", url=f"https://t.me/EXProjects"
                    )
                ]
            ]
        ),
    ) 

@Client.on_message(command(["uptime", f"uptime@{BOT_USERNAME}"]) & ~filters.edited)
@authorized_users_only
async def get_uptime(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        "🤖 bot status:\n"
        f"• **uptime:** `{uptime}`\n"
        f"• **start time:** `{START_TIME_ISO}`",
      reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Group Support", url=f"https://t.me/EXGroupSupport"
                    )
                ]
            ]
        ),
    )


@Client.on_message(filters.command(["alive", f"alive@{BOT_USERNAME}"]))
async def alive(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_photo(
        photo=f"https://telegra.ph/file/375e7d9b3dd70a3431418.jpg",
        caption=f"""**• Holla I'm [{BOT_NAME}](https://t.me/{BOT_USERNAME})**
• **I'm Working Properly**
• **Bot : 6.5 LATEST**
• **My Master : [EX](https://t.me/rizexx)**
• **Service Uptime : `{uptime}`**
**Thanks For Using Me ♡**""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🚨 Group", url=f"https://t.me/EXSupportGroup"
                    ),
                    InlineKeyboardButton(
                        "📡 Channel", url=f"https://t.me/EXProjects"
                    )
                ]
            ]
        )
    )
