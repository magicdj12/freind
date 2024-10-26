import asyncio
import logging

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.types import CallbackQuery, Message

from config import BANNED_USERS, adminlist, lyrical
from strings import get_command
from YukkiMusic import app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import db
from YukkiMusic.utils.database import get_authuser_names, get_cmode
from YukkiMusic.utils.decorators import ActualAdminCB, AdminActual, language
from YukkiMusic.utils.formatters import alpha_to_int

### Multi-Lang Commands
RELOAD_COMMAND = get_command("RELOAD_COMMAND")
REBOOT_COMMAND = get_command("REBOOT_COMMAND")


@app.on_message(filters.command(RELOAD_COMMAND , prefixes=["", "/"]) & filters.group & ~BANNED_USERS)
@language
async def reload_admin_cache(client, message: Message, _):
    try:
        chat_id = message.chat.id
        admins = app.get_chat_members(chat_id, filter=ChatMembersFilter.ADMINISTRATORS)
        authusers = await get_authuser_names(chat_id)
        adminlist[chat_id] = []
        async for user in admins:
            if user.privileges.can_manage_video_chats:
                adminlist[chat_id].append(user.user.id)
        for user in authusers:
            user_id = await alpha_to_int(user)
            adminlist[chat_id].append(user_id)
        await message.reply_text(_["admin_20"])
    except:
        await message.reply_text(
            "لود دوباره ادمین به مشکل مواجه شد از مدیر بودن ربات خودرا مطما کنید."
        )


@app.on_message(filters.command(REBOOT_COMMAND , prefixes=["", "/"]) & filters.group & ~BANNED_USERS)
@AdminActual
async def restartbot(client, message: Message, _):
    mystic = await message.reply_text(
        f"لطفا صبر کنید .. \nشورع دوباره {app.mention} برای چت شما.."
    )
    await asyncio.sleep(1)
    try:
        db[message.chat.id] = []
        await Yukki.stop_stream(message.chat.id)
    except:
        pass
    chat_id = await get_cmode(message.chat.id)
    if chat_id:
        try:
            await app.get_chat(chat_id)
        except:
            pass
        try:
            db[chat_id] = []
            await Yukki.stop_stream(chat_id)
        except:
            pass
    return await mystic.edit_text("موفقانه شروع شد. \nحالا دوباره پخش کنید..")


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except Exception as e:
        logging.exception(e)
        try:
            await app.delete_messages(
                chat_id=CallbackQuery.message.chat.id,
                message_ids=CallbackQuery.message.id,
            )
        except Exception as e:
            logging.exception(e)
            return


@app.on_callback_query(filters.regex("close") & ~BANNED_USERS)
async def close_menu(_, CallbackQuery):
    try:
        await CallbackQuery.message.delete()
        await CallbackQuery.answer()
    except:
        return


@app.on_callback_query(filters.regex("stop_downloading") & ~BANNED_USERS)
@ActualAdminCB
async def stop_download(client, CallbackQuery: CallbackQuery, _):
    message_id = CallbackQuery.message.id
    task = lyrical.get(message_id)
    if not task:
        return await CallbackQuery.answer(
            "دانلود از قبل تمام شده است..", show_alert=True
        )
    if task.done() or task.cancelled():
        return await CallbackQuery.answer(
            "دانلود از قبل تمام شده یا لغوه شده است.",
            show_alert=True,
        )
    if not task.done():
        try:
            task.cancel()
            try:
                lyrical.pop(message_id)
            except:
                pass
            await CallbackQuery.answer("دانلود لغوه شده است ", show_alert=True)
            return await CallbackQuery.edit_message_text(
                f"دانلود لغوه شده است  توسط {CallbackQuery.from_user.mention}"
            )
        except:
            return await CallbackQuery.answer(
                "توفق دانلود به شکست مواجه شد", show_alert=True
            )

    await CallbackQuery.answer("شکست در تشخیص تسک در حال اجرا", show_alert=True)
