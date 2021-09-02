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
from EXmusic.modules.msg import Messages as tr
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
    filters.command(["start", f"start@{BOT_USERNAME}"])
    & filters.private
    & ~ filters.edited
)
async def start_(client: Client, message: Message):
    await message.reply_text(
        f"""<b>👋 **𝗪𝗲𝗹𝗰𝗼𝗺𝗲** {message.from_user.mention()}**\n
💭 [𝗘𝗫 𝗠𝘂𝘀𝗶𝗰](https://t.me/{BOT_USERNAME}) 𝗮𝗹𝗹𝗼𝘄 𝘆𝗼𝘂 𝘁𝗼 𝗽𝗹𝗮𝘆 𝗺𝘂𝘀𝗶𝗰 𝗼𝗻 𝗴𝗿𝗼𝘂𝗽𝘀 𝘁𝗵𝗿𝗼𝘂𝗴𝗵 𝘁𝗵𝗲 𝗻𝗲𝘄 𝗧𝗲𝗹𝗲𝗴𝗿𝗮𝗺'𝘀 𝘃𝗼𝗶𝗰𝗲 𝗰𝗵𝗮𝘁𝘀!
💡 𝗖𝗹𝗶𝗰𝗸 [𝗵𝗲𝗿𝗲](https://t.me/{BOT_USERNAME}?startgroup=true) 𝘁𝗼 𝗮𝗱𝗱 𝗺𝗲 𝘁𝗼 𝘆𝗼𝘂𝗿 𝗴𝗿𝗼𝘂𝗽!

❔ 𝗙𝗼𝗿 𝗶𝗻𝗳𝗼𝗿𝗺𝗮𝘁𝗶𝗼𝗻 𝗮𝗯𝗼𝘂𝘁 𝗮𝗹𝗹 𝗳𝗲𝗮𝘁𝘂𝗿𝗲 𝗼𝗳 𝘁𝗵𝗶𝘀 𝗯𝗼𝘁, 𝗷𝘂𝘀𝘁 𝘁𝘆𝗽𝗲 /help
<b>""",

        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏺️ Official Channel", url=f"https://t.me/EXProjects"), 
                    InlineKeyboardButton(
                        "👥 Support Group", url=f"https://t.me/EXGroupSupport")
                ],[
                    InlineKeyboardButton(
                        "👩‍💻 Created by", url=f"https://t.me/rizexx")
                ]
            ]
        ),
        disable_web_page_preview=True
        )

@Client.on_message(filters.private & filters.incoming & filters.command(['help']))
def _help(client, message):
    client.send_message(chat_id = message.chat.id,
        text = tr.HELP_MSG[1],
        parse_mode="markdown",
        disable_web_page_preview=True,
        disable_notification=True,
        reply_markup = InlineKeyboardMarkup(map(1)),
        reply_to_message_id = message.message_id
    )

help_callback_filter = filters.create(lambda _, __, query: query.data.startswith('help+'))

@Client.on_callback_query(help_callback_filter)
def help_answer(client, callback_query):
    chat_id = callback_query.from_user.id
    disable_web_page_preview=True
    message_id = callback_query.message.message_id
    msg = int(callback_query.data.split('+')[1])
    client.edit_message_text(chat_id=chat_id,    message_id=message_id,
        text=tr.HELP_MSG[msg],    reply_markup=InlineKeyboardMarkup(map(msg))
    )


def map(pos):
    if(pos==1):
        button = [
            [
              InlineKeyboardButton(text = 'About bot ❔', callback_data = "help+2"),
              InlineKeyboardButton(text = 'Commands 📚', url=f"https://telegra.ph/PGuide-to-using-EXMUSIC-bot-08-13"),
              InlineKeyboardButton(text = 'Back', callback_data = "start")],
        ]
    elif(pos==len(tr.HELP_MSG)-1):
        url = f"https://t.me/EXGroupSupport"
        button = [
            [InlineKeyboardButton(text = '⏺️ Official Channel', url=f"https://t.me/EXProject"),
             InlineKeyboardButton(text = '👥 Support Group', url=f"https://t.me/EXGroupSupport")],
            [InlineKeyboardButton(text = 'Back «', callback_data = f"help+{pos-1}")]
        ]
    else:
        button = [
            [
                InlineKeyboardButton(text = '«', callback_data = f"help+{pos-1}"),
                InlineKeyboardButton(text = '»', callback_data = f"help+{pos+1}")
            ],
        ]
    return button


@Client.on_message(
    filters.command(["start", f"start@{BOT_USERNAME}"])
    & filters.group
    & ~ filters.edited
)
async def start(client: Client, message: Message):
    current_time = datetime.utcnow()
    uptime_sec = (current_time - START_TIME).total_seconds()
    uptime = await _human_time_duration(int(uptime_sec))
    await message.reply_text(
        f"""✅ **bot is running Successful**\n\n<b>• **uptime:**</b> `{uptime}`\n• **start time:** `{START_TIME_ISO}`""",
        reply_markup=InlineKeyboardMarkup(
            [   
                [    
                    InlineKeyboardButton(
                        "👥 Group", url=f"https://t.me/EXGroupSupport"
                    ),
                    InlineKeyboardButton(
                        "⏺️ Channel", url=f"https://t.me/EXProjects"
                    )
                ]
            ]
        )
    )

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

@Client.on_message(command("help") & filters.private & ~filters.edited)
async def help_(client: Client, message: Message):
    await message.reply_text(
        f"""<b>👋 Hello {message.from_user.mention} welcome to the help menu !</b>
**in this menu you can open several available command menus**\n\n in each **command** menu there is also a brief **explanation** of each command.\n🎛️ **Powered by** EX Music bot.""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "📚 Basic", callback_data="cbbasic"
                    ),
                    InlineKeyboardButton(
                        "📕 Advanced", callback_data="cbadvanced"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📘 Admin Commands", callback_data="cbadmin"
                    ),
                    InlineKeyboardButton(
                        "📗 Sudo Commands", callback_data="cbsudo"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📙 Owner Commands", callback_data="cbowner"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📔 Fun Commands", callback_data="cbfun"
                    )
                ]
            ]
        )
    )

@Client.on_message(
    filters.command("reload")
    & filters.group
    & ~ filters.edited
)
async def reload(client: Client, message: Message):
    await message.reply_text("""✅ Bots **Successful restart!**\n\n• **Admin list** Has been successfully **updated**""",
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

@Client.on_message(command(["ping", f"ping@{BOT_USERNAME}"]) & ~filters.edited)
async def ping_pong(client: Client, message: Message):
    start = time()
    m_reply = await message.reply_text("pinging...")
    delta_ping = time() - start
    await m_reply.edit_text(
        "🏓 `PONG!!`\n"
        f"⚡️ `{delta_ping * 1000:.3f} ms`"
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
        f"• **start time:** `{START_TIME_ISO}`"
    )
