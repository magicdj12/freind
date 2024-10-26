from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, LOG_GROUP_ID
from YukkiMusic import app
from YukkiMusic.core.userbot import assistants
from YukkiMusic.utils.assistant import get_assistant_details
from YukkiMusic.utils.assistant import is_avl_assistant as assistant
from YukkiMusic.utils.database import get_assistant, save_assistant, set_assistant
from YukkiMusic.utils.decorators import AdminActual


@app.on_message(filters.command("changeassistant" , prefixes=["", "/"]) & ~BANNED_USERS)
@AdminActual
async def assis_change(client, message: Message, _):
    if await assistant() == True:
        return await message.reply_text(
            "متاسفم! در سرور ربات فقط دستیار آنلاین موجود است، بنابراین شما نمی‌توانید دستیار را تغییر دهید."
        )
    usage = f"**به نظر می‌رسد که شما از یک دستور نادرست استفاده کرده‌اید. لطفاً توجه داشته باشید که:دستور:/changeassistant - تغییر دستیار فعلی شما به یک دستیار تصادفی در سرور بات."
    if len(message.command) > 2:
        return await message.reply_text(usage)
    a = await get_assistant(message.chat.id)
    DETAILS = f"دستیار صوتی شما تغیر کرد [{a.name}](https://t.me/{a.username}) "
    if not message.chat.id == LOG_GROUP_ID:
        try:
            await a.leave_chat(message.chat.id)
        except:
            pass
    b = await set_assistant(message.chat.id)
    DETAILS += f"ᴛᴏ [{b.name}](https://t.me/{b.username})"
    try:
        await b.join_chat(message.chat.id)
    except:
        pass
    await message.reply_text(DETAILS, disable_web_page_preview=True)


@app.on_message(filters.command("setassistant" , prefixes=["", "/"]) & ~BANNED_USERS)
@AdminActual
async def assis_set(client, message: Message, _):
    if await assistant():
        return await message.reply_text(
            "متأسفم، آقا! در سرور ربات فقط یک دستیار موجود است، بنابراین شما نمی‌توانید دستیار را تغییر دهید."
        )
    usage = await get_assistant_details()
    if len(message.command) != 2:
        return await message.reply_text(usage, disable_web_page_preview=True)
    query = message.text.split(None, 1)[1].strip()
    if query not in assistants:
        return await message.reply_text(usage, disable_web_page_preview=True)
    a = await get_assistant(message.chat.id)
    try:
        await a.leave_chat(message.chat.id)
    except:
        pass
    await save_assistant(message.chat.id, query)
    b = await get_assistant(message.chat.id)
    try:
        await b.join_chat(message.chat.id)
    except:
        pass
    await message.reply_text(
        "**مشخصات دستیار صوتی شما:**\nنام دستیار صوتی شما  :- {b.name}\nنام کاربری :- @{b.username}\nایدی :- {b.id}",
        disable_web_page_preview=True,
    )


@app.on_message(filters.command("checkassistant" , prefixes=["", "/"]) & filters.group & ~BANNED_USERS)
@AdminActual
async def check_ass(client, message: Message, _):
    a = await get_assistant(message.chat.id)
    await message.reply_text(
        "**مشخصات دستیار صوتی:**\nنام دستیار صوتی شما  :- {a.name}\nدستیار صوتی\nنام کاربری :- @{a.username}\nایدی دستیار صوتی:- {a.id}",
        disable_web_page_preview=True,
    )
