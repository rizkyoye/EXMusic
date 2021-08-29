# Copyright (C) 2021 EXMusicbot

import traceback
import asyncio
from asyncio import QueueEmpty
from EXmusic.config import que
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, Chat, CallbackQuery, ChatPermissions

from EXmusic.function.admins import admins
from EXmusic.helpers.channelmusic import get_chat_id
from EXmusic.helpers.decorators import authorized_users_only, errors
from EXmusic.modules.play import cb_admin_check
from EXmusic.helpers.filters import command, other_filters
from EXmusic.services.callsmusic import callsmusic
from EXmusic.services.callsmusic import queues
from EXmusic.config import LOG_CHANNEL, OWNER, BOT_USERNAME, COMMAND_PREFIXES
from EXmusic.helpers.database import db, dcmdb, Database
from EXmusic.helpers.dbtools import handle_user_status, delcmd_is_on, delcmd_on, delcmd_off
from EXmusic.helpers.helper_functions.admin_check import admin_check
from EXmusic.helpers.helper_functions.extract_user import extract_user
from EXmusic.helpers.helper_functions.string_handling import extract_time


@Client.on_message()
async def _(bot: Client, cmd: Message):
    await handle_user_status(bot, cmd)

# Back Button
BACK_BUTTON = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 go back", callback_data="cbback")]])

@Client.on_message(filters.text & ~filters.private)
async def delcmd(_, message: Message):
    if await delcmd_is_on(message.chat.id) and message.text.startswith("/") or message.text.startswith("!"):
        await message.delete()
    await message.continue_propagation()


@Client.on_message(filters.command("reload"))
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text("✅ Bot **reloaded correctly !**\n✅ **Admin list** has been **updated !**")


# Control Menu Of Player
@Client.on_message(command(["control", f"control@{BOT_USERNAME}", "p"]))
@errors
@authorized_users_only
async def controlset(_, message: Message):
    await message.reply_text(
        "**💡 opened music player control menu!**\n\n📝 You can control the **music player** just by pressing one of the buttons **below**\n\n📣 **Updates Chanmel :** @EXProjects",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "⏸ pause", callback_data="cbpause"
                    ),
                    InlineKeyboardButton(
                        "▶️ resume", callback_data="cbresume"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⏩ skip", callback_data="cbskip"
                    ),
                    InlineKeyboardButton(
                        "⏹ end", callback_data="cbend"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⛔ anti cmd", callback_data="cbdelcmds"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🛄 group tools", callback_data="cbgtools"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Close", callback_data="close"
                    )
                ]
            ]
        )
    )


@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "paused"
    ):
        await message.reply_text("❎ No song is playing!")
    else:
        callsmusic.pytgcalls.pause_stream(chat_id)
        await message.reply_text("▶️ **Music paused!**\n\n• For resuming the song, use command » /resume")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if (chat_id not in callsmusic.pytgcalls.active_calls) or (
        callsmusic.pytgcalls.active_calls[chat_id] == "playing"
    ):
        await message.reply_text("❎ Nothing is paused!")
    else:
        callsmusic.pytgcalls.resume_stream(chat_id)
        await message.reply_text("⏸ **Music resumed!**\n\n• For end the song, use command » /end")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❎ Nothing is streaming!")
    else:
        try:
            queues.clear(chat_id)
        except QueueEmpty:
            pass

        callsmusic.pytgcalls.leave_group_call(chat_id)
        await message.reply_text("✅ **Streaming ended**\n\n• Assistant has been disconnected from voice chat group")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    chat_id = get_chat_id(message.chat)
    if chat_id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❎ Nothing is playing to skip!\n\n**Info Update** : @EXProjects")
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
    await message.reply_text(f"💡 **You jump to the next song queue..**\n ┈────────────────────┈\n• skipped : **{skip[0]}**\n• now playing : **{qeue[0][0]}**")


@Client.on_message(command("auth") & other_filters)
@authorized_users_only
async def authenticate(client, message):
    global admins
    if not message.reply_to_message:
        await message.reply("❗ reply to message to authorize user!")
        return
    if message.reply_to_message.from_user.id not in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.append(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply("🟢 user authorized.\n\nfrom now on, that's user can use the admin commands.")
    else:
        await message.reply("✅ user already authorized!")


@Client.on_message(command("deauth") & other_filters)
@authorized_users_only
async def deautenticate(client, message):
    global admins
    if not message.reply_to_message:
        await message.reply("❗ reply to message to deauthorize user!")
        return
    if message.reply_to_message.from_user.id in admins[message.chat.id]:
        new_admins = admins[message.chat.id]
        new_admins.remove(message.reply_to_message.from_user.id)
        admins[message.chat.id] = new_admins
        await message.reply("🔴 user deauthorized.\n\nfrom now that's user can't use the admin commands.")
    else:
        await message.reply("✅ user already deauthorized!")


# this is a anti cmd feature
@Client.on_message(command(["delcmd", f"delcmd@{BOT_USERNAME}"]) & ~filters.private)
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
            await message.reply_text("✅ already activated")
            return
        else:
            await delcmd_on(chat_id)
            await message.reply_text(
                "🟢 activated successfully"
            )
    elif status == "off":
        await delcmd_off(chat_id)
        await message.reply_text("🔴 disabled successfully")
    else:
        await message.reply_text(
            "read the /help message to know how to use this command"
        )


# music player callbacks (control by buttons feature)

@Client.on_callback_query(filters.regex("cbpause"))
@cb_admin_check
async def cbpause(_, query: CallbackQuery):
    chat_id = get_chat_id(query.message.chat)
    if (
        query.message.chat.id not in callsmusic.pytgcalls.active_calls
            ) or (
                callsmusic.pytgcalls.active_calls[query.message.chat.id] == "paused"
            ):
        await query.edit_message_text("❎ nothing is playing", reply_markup=BACK_BUTTON)
    else:
        callsmusic.pytgcalls.pause_stream(query.message.chat.id)
        await query.edit_message_text("▶️ Music stopped! **you're sorry**", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbresume"))
@cb_admin_check
async def cbresume(_, query: CallbackQuery):
    chat_id = get_chat_id(query.message.chat)
    if (
        query.message.chat.id not in callsmusic.pytgcalls.active_calls
            ) or (
                callsmusic.pytgcalls.active_calls[query.message.chat.id] == "resumed"
            ):
        await query.edit_message_text("❎ nothing is paused", reply_markup=BACK_BUTTON)
    else:
        callsmusic.pytgcalls.resume_stream(query.message.chat.id)
        await query.edit_message_text("⏸ music is resumed", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbend"))
@cb_admin_check
async def cbend(_, query: CallbackQuery):
    chat_id = get_chat_id(query.message.chat)
    if query.message.chat.id not in callsmusic.pytgcalls.active_calls:
        await query.edit_message_text("❎ nothing is playing", reply_markup=BACK_BUTTON)
    else:
        try:
            queues.clear(query.message.chat.id)
        except QueueEmpty:
            pass
        
        callsmusic.pytgcalls.leave_group_call(query.message.chat.id)
        await query.edit_message_text("✅ the music queue has been cleared and successfully left voice chat", reply_markup=BACK_BUTTON)

@Client.on_callback_query(filters.regex("cbskip"))
@cb_admin_check
async def cbskip(_, query: CallbackQuery):
    global que
    chat_id = get_chat_id(query.message.chat)
    if query.message.chat.id not in callsmusic.pytgcalls.active_calls:
        await query.edit_message_text("❎ nothing is playing", reply_markup=BACK_BUTTON)
    else:
        queues.task_done(query.message.chat.id)
        
        if queues.is_empty(query.message.chat.id):
            callsmusic.pytgcalls.leave_group_call(query.message.chat.id)
        else:
            callsmusic.pytgcalls.change_stream(
                query.message.chat.id, queues.get(query.message.chat.id)["file"]
            )
            
    qeue = que.get(chat_id)
    if qeue:
        skip = qeue.pop(0)
    if not qeue:
        return
    await query.edit_message_text(f"⏭ skipped music\n\n» skipped : **{skip[0]}**\n» now playing : **{qeue[0][0]}**", reply_markup=BACK_BUTTON)

# (C) Veez Music Project

# ban & unban function

@Client.on_message(filters.command("b", COMMAND_PREFIXES))
@authorized_users_only
async def ban_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    user_id, user_first_name = extract_user(message)

    try:
        await message.chat.kick_member(
            user_id=user_id
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "✅ successfully banned "
                f"{user_first_name}"
                " from this group !"
            )
        else:
            await message.reply_text(
                "✅ banned "
                f"<a href='tg://user?id={user_id}'>"
                f"{user_first_name}"
                "</a>"
                " from this group !"
            )


@Client.on_message(filters.command("tb", COMMAND_PREFIXES))
@authorized_users_only
async def temp_ban_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    if not len(message.command) > 1:
        return

    user_id, user_first_name = extract_user(message)

    until_date_val = extract_time(message.command[1])
    if until_date_val is None:
        await message.reply_text(
            (
                "the specified time type is invalid. "
                "use m, h, or d, format time: {}"
            ).format(
                message.command[1][-1]
            )
        )
        return

    try:
        await message.chat.kick_member(
            user_id=user_id,
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "✅ temporarily banned "
                f"{user_first_name}"
                f" ,banned for {message.command[1]}!"
            )
        else:
            await message.reply_text(
                "✅ temporarily banned "
                f"<a href='tg://user?id={user_id}'>"
                "from this group !"
                "</a>"
                f" ,banned for {message.command[1]}!"
            )

@Client.on_message(filters.command(["ub", "um"], COMMAND_PREFIXES))
@authorized_users_only
async def un_ban_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    user_id, user_first_name = extract_user(message)

    try:
        await message.chat.unban_member(
            user_id=user_id
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "ok accepted, user "
                f"{user_first_name} to "
                " can join to this group again!"
            )
        else:
            await message.reply_text(
                "ok, now "
                f"<a href='tg://user?id={user_id}'>"
                f"{user_first_name}"
                "</a> can "
                " join to this group again!"
            )

@Client.on_message(filters.command("m", COMMAND_PREFIXES))
async def mute_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    user_id, user_first_name = extract_user(message)

    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            )
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "✅ okay,🏻 "
                f"{user_first_name}"
                " successfully muted !"
            )
        else:
            await message.reply_text(
                "🏻✅ okay, "
                f"<a href='tg://user?id={user_id}'>"
                "now is"
                "</a>"
                " muted !"
            )


@Client.on_message(filters.command("tm", COMMAND_PREFIXES))
async def temp_mute_user(_, message):
    is_admin = await admin_check(message)
    if not is_admin:
        return

    if not len(message.command) > 1:
        return

    user_id, user_first_name = extract_user(message)

    until_date_val = extract_time(message.command[1])
    if until_date_val is None:
        await message.reply_text(
            (
                "The specified time type is invalid. "
                "use m, h, or d, format time: {}"
            ).format(
                message.command[1][-1]
            )
        )
        return

    try:
        await message.chat.restrict_member(
            user_id=user_id,
            permissions=ChatPermissions(
            ),
            until_date=until_date_val
        )
    except Exception as error:
        await message.reply_text(
            str(error)
        )
    else:
        if str(user_id).lower().startswith("@"):
            await message.reply_text(
                "Muted for a while! "
                f"{user_first_name}"
                f" muted for {message.command[1]}!"
            )
        else:
            await message.reply_text(
                "Muted for a while! "
                f"<a href='tg://user?id={user_id}'>"
                "is"
                "</a>"
                " now "
                f" muted, for {message.command[1]}!"
            )
