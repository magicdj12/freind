import os
from inspect import getfullargspec

from pyrogram import filters
from pyrogram.types import Message

from YukkiMusic import app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database import get_client


@app.on_message(filters.command("setpfp", prefixes=["", "/"]) & SUDOERS)
async def set_pfp(client, message):
    from YukkiMusic.core.userbot import assistants

    if not message.reply_to_message or not message.reply_to_message.photo:
        return await eor(message, text="به عکس ریپلای کنید")
    for num in assistants:
        client = await get_client(num)
        photo = await message.reply_to_message.download()
        try:
            await client.set_profile_photo(photo=photo)
            await eor(message, text="موفقانه تغیر یافت .")
            os.remove(photo)
        except Exception as e:
            await eor(message, text=e)
            os.remove(photo)


@app.on_message(filters.command("setbio", prefixes=".") & SUDOERS)
async def set_bio(client, message):
    from YukkiMusic.core.userbot import assistants

    if len(message.command) == 1:
        return await eor(message, text="همراه یک متن بفرستید برای بیو")
    elif len(message.command) > 1:
        for num in assistants:
            client = await get_client(num)
            bio = message.text.split(None, 1)[1]
        try:
            await client.update_profile(bio=bio)
            await eor(message, text="بیو تغیر کرد.")
        except Exception as e:
            await eor(message, text=e)
    else:
        return await eor(message, text="همراه یک متن بفرستید برای بیو")


@app.on_message(filters.command("setname", prefixes=".") & SUDOERS)
async def set_name(client, message):
    from YukkiMusic.core.userbot import assistants

    if len(message.command) == 1:
        return await eor(message, text="همراه یک نام بفرستید برای اسم ربات")
    elif len(message.command) > 1:
        for num in assistants:
            client = await get_client(num)
            name = message.text.split(None, 1)[1]
        try:
            await client.update_profile(first_name=name)
            await eor(message, text=f"نام تغیر کرد به  {name} .")
        except Exception as e:
            await eor(message, text=e)
    else:
        return await eor(message, text="همراه یک نام بفرستید برای اسم ربات")


@app.on_message(filters.command("delpfp", prefixes=".") & SUDOERS)
async def del_pfp(client, message):
    from YukkiMusic.core.userbot import assistants

    for num in assistants:
        client = await get_client(num)
        photos = [p async for p in client.get_chat_photos("me")]
        try:
            if photos:
                await client.delete_profile_photos(photos[0].file_id)
                await eor(message, text="موفقانه عکس حذف گردید ")
            else:
                await eor(message, text="پروفایلی پیدا نشد.")
        except Exception as e:
            await eor(message, text=e)


@app.on_message(filters.command("delallpfp", prefixes=".") & SUDOERS)
async def delall_pfp(client, message):
    from YukkiMusic.core.userbot import assistants

    for num in assistants:
        client = await get_client(num)
        photos = [p async for p in client.get_chat_photos("me")]
        try:
            if photos:
                await client.delete_profile_photos([p.file_id for p in photos[1:]])
                await eor(message, text="موفقانه عکس حذف گردید ")
            else:
                await eor(message, text="پروفایلی پیدا نشد.")
        except Exception as e:
            await eor(message, text=e)


async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})


"""
<u>دستورات دستیار:</u>
.setpfp - پاسخ به عکس برای تنظیم عکس پروفایل تمام دستیارهای ربات [فقط عکس] [فقط برای کاربر سودو]

.setname [متن] - برای تنظیم نام تمام دستیارهای ربات [فقط برای کاربر سودو]

.setbio [متن] - برای تنظیم بیوگرافی تمام دستیارهای ربات [فقط برای کاربر سودو]

.delpfp - حذف عکس پروفایل دستیار ربات [فقط یک عکس پروفایل حذف خواهد شد] [فقط برای کاربر سودو]

.delallpfp - حذف تمام عکس‌های پروفایل دستیار ربات [فقط یک عکس پروفایل باقی خواهد ماند] [فقط برای کاربر سودو]

<u>دستورات دستیار گروه:</u>

/checkassistant - بررسی جزئیات دستیار گروه شما

/setassistant - تغییر دستیار به یک دستیار خاص برای گروه شما

/changeassistant - تغییر دستیار گروه شما به یک دستیار تصادفی موجود در سرور ربات
"""
