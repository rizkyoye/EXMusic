# (C) supun-maduraga my best friend for his project on call-music-plus

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Chat, CallbackQuery
from EXmusic.config import BOT_NAME
from EXmusic.services.callsmusic.kalmusik import client as USER


# close calllback

@Client.on_callback_query(filters.regex("close"))
async def close(_, query: CallbackQuery):
    await query.message.delete()

# Player Control Callbacks

@Client.on_callback_query(filters.regex("cbback"))
async def cbback(_, query: CallbackQuery):
    await query.edit_message_text(
        "🎛️ **here is the control menu of bot:**",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ᴘᴀᴜsᴇ", callback_data="cbpause"
                    ),
                    InlineKeyboardButton(
                        "ʀᴇsᴜᴍᴇ", callback_data="cbresume"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "sᴋɪᴘ", callback_data="cbskip"
                    ),
                    InlineKeyboardButton(
                        "ᴇɴᴅ", callback_data="cbend"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "ᴍᴜᴛᴇ", callback_data="cbmute"
                    ),
                    InlineKeyboardButton(
                        "ᴜɴᴍᴜᴛᴇ", callback_data="cbunmute"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "ᴅᴇʟ ᴄᴍᴅ", callback_data="cbdelcmds"
                    )
                ]
            ]
        )
    )


@Client.on_callback_query(filters.regex("cbdelcmds"))
async def cbdelcmds(_, query: CallbackQuery):
    await query.edit_message_text(
        f"""<b>this is the feature information:</b>
        
**💡 Feature:** delete every commands sent by users to avoid spam !

**❔ usage:**

   1️⃣ to turn on feature:
      - type /delcmd on
    
   2️⃣ to turn off feature:
      - type /delcmd off
      
⚡ __Powered by {BOT_NAME} A.I__""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "ʙᴀᴄᴋ", callback_data="cbback"
                    )
                ]
            ]
        )
    )
