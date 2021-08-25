# Copyright (C) 2021 VeezMusicProject

import traceback
import asyncio

from asyncio import QueueEmpty
from EXmusic.config import que
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Chat, CallbackQuery

from EXmusic.function.admins import admins
from EXmusic.helpers.channelmusic import get_chat_id
from EXmusic.helpers.decorators import errors, authorized_users_only
from EXmusic.helpers.filters import command, other_filters
from EXmusic.services.callsmusic.callsmusic import queues
from EXmusic.config import LOG_CHANNEL, OWNER, BOT_USERNAME
from EXmusic.helpers.database import db, dcmdb, Database
from EXmusic.helpers.dbtools import handle_user_status, delcmd_is_on, delcmd_on, delcmd_off
from EXmusic.modules.admins import que, admins
from EXmusic.services.callsmusic import callsmusic
from EXmusic.services.queues import queues

# Credit ©️ Rizky ganteng

@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text("❎ **No song is playing**")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await message.reply_text("❗ **Music paused!**\n\nTo resume music use **Command** » `/resume`")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text("❎ *No song is playing to stop!**")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text("⏸ **Music resumed!**\n\nTo stop the song use the **Command** » `/stop`")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❎ **nothing in streaming!**")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("✅ **Streaming ended!**\n\n**Assistant has been disconnected from voice chat group**")

@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ **Nothing in streaming!**")
    else:
        queues.task_done(chat_id)

        if queues.is_empty(chat_id):
            callsmusic.pytgcalls.leave_group_call(chat_id)
        else:
            callsmusic.pytgcalls.change_stream(
                chat_id, queues.get(chat_id)["file"]
            )

    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await message.reply_text(f"• skipped : **{skip[0]}**\n√ now playing : **{qeue[0][0]}**")


@Client.on_message(filters.command("reload"))
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text("✅ Bot **reloaded correctly !**\n✅ **Admin list** has been **updated !**")

# Khontolss

@Client.on_message()
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)

# Back Button
BACK_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="cbback")]])

@Client.on_message(filters.text & ~filters.private)
async def delcmd(_, message: Message):
    if await delcmd_is_on(message.chat.id) and message.text.startswith("/") or message.text.startswith("!"):
        await message.delete()
    await message.continue_propagation()

# Control Menu Of Player
@Client.on_message(command(["control"]))
@errors
@authorized_users_only
async def controlset(_, message: Message):
    await message.reply_text(
        "💡 **here is the control menu of bot :**",
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
                        "ᴜɴᴍᴜᴛᴇ ᴘʟᴀʏ", callback_data="cbunmute"
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


@Client.on_message(filters.command("auth"))
@authorized_users_only
async def authenticate(client, message):
    global admins
    if not message.reply_to_message:
        await message.reply("❎ reply to message to **authorize user!**")
        return
    if message.reply_to_message.from_user.id not in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.append(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply("🟢 user authorized.\n\nfrom now on, that's user can use the admin **commands.**")
    else:
        await message.reply("✅ **User already authorized!**")


@Client.on_message(filters.command("deauth"))
@authorized_users_only
async def deautenticate(client, message):
    global admins
    if not message.reply_to_message:
        await message.reply("❎ reply to message to deauthorize user!")
        return
    if message.reply_to_message.from_user.id in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.remove(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply("🔴 user deauthorized.\n\nfrom now that's user can't use the admin **commands.**")
    else:
        await message.reply("✅ user already deauthorized!")


# this is a anti cmd feature
@Client.on_message(filters.command(["delcmd"]) & ~filters.private)
@authorized_users_only
async def delcmdc(_, message: Message):
    if len(message.command) != 2:
        await message.reply_text("read the /help message to know how to use this command")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status == "on":
        if await delcmd_is_on(message.chat.id):
            await message.reply_text("✅ **already activated**")
            return
        else:
            await delcmd_on(chat_id)
            await message.reply_text(
                "✅ **Activated successfully!**"
            )
    elif status == "off":
        await delcmd_off(chat_id)
        await message.reply_text("✅ **Disabled successfully**")
    else:
        await message.reply_text(
            "read the /help message to know how to use this command"
        )


@Client.on_message(command(["silent"]))
@errors
@authorized_users_only
async def silent(_, message: Message):
    result = callsmusic.mute(message.chat.id)

    if result == 0:
        await message.reply_text("`Assistant muted`")
    elif result == 1:
        await message.reply_text("✅ **assistant already muted**")
    elif result == 2:
        await message.reply_text("❎ **not connected to voice chat**")


@Client.on_message(command(["unsilent"]))
@errors
@authorized_users_only
async def unsilent(_, message: Message):
    result = callsmusic.unmute(message.chat.id)

    if result == 0:
        await message.reply_text("`Assistant unmuted`")
    elif result == 1:
        await message.reply_text("✅ **assistant already unmuted**")
    elif result == 2:
        await message.reply_text("❎ **not connected to voice chat**")


# music player callbacks (control by buttons feature)

@Client.on_callback_query(filters.regex("cbpause") & other_filters)
async def cbpause(_, query: CallbackQuery):
    if callsmusic.pause(query.message.chat.id):
        await query.edit_message_text("⏸ Music has been temporarily suspended!", reply_markup=BACK_BUTTON)
    else:
        await query.edit_message_text("❗️ nothing is playing", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbresume") & other_filters)
async def cbresume(_, query: CallbackQuery):
    if callsmusic.resume(query.message.chat.id):
        await query.edit_message_text("▶ music resumed", reply_markup=BACK_BUTTON)
    else:
        await query.edit_message_text("❗️ nothing is paused", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbend") & other_filters)
async def cbend(_, query: CallbackQuery):
    if query.message.chat.id not in callsmusic.active_chats:
        await query.edit_message_text("❗️ nothing is playing", reply_markup=BACK_BUTTON)
    else:
        try:
            queues.clear(query.message.chat.id)
        except QueueEmpty:
            pass

        await callsmusic.stop(query.message.chat.id)
        await query.edit_message_text("✅ cleared the queue and left the voice chat!", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbskip") & other_filters)
async def cbskip(_, query: CallbackQuery):
     if query.message.chat.id not in callsmusic.active_chats:
        await query.edit_message_text("❗️ nothing is playing", reply_markup=BACK_BUTTON)
     else:
        queues.task_done(query.message.chat.id)
        
        if queues.is_empty(query.message.chat.id):
            await callsmusic.stop(query.message.chat.id)
        else:
            await callsmusic.set_stream(
                query.message.chat.id, queues.get(query.message.chat.id)["file"]
            )

        await query.edit_message_text("⏭ skipped to the next music", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbmute") & other_filters)
async def cbmute(_, query: CallbackQuery):
    result = callsmusic.mute(query.message.chat.id)

    if result == 0:
        await query.edit_message_text("🔇 assistant muted", reply_markup=BACK_BUTTON)
    elif result == 1:
        await query.edit_message_text("✅ assistant already muted", reply_markup=BACK_BUTTON)
    elif result == 2:
        await query.edit_message_text("❗️ not connected to voice chat", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbunmute") & other_filters)
async def cbunmute(_, query: CallbackQuery):
    result = callsmusic.unmute(query.message.chat.id)

    if result == 0:
        await query.edit_message_text("🔊 assistant unmuted", reply_markup=BACK_BUTTON)
    elif result == 1:
        await query.edit_message_text("✅ assistant already unmuted", reply_markup=BACK_BUTTON)
    elif result == 2:
        await query.edit_message_text("❗️ not connected to voice chat", reply_markup=BACK_BUTTON)

# (C) supun-maduraga for his project on call-music-plus 
