from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

import config
from YukkiMusic import app

TEXT = f"""
🔒
سلام!  
ما در شرکت آترو اهمیت زیادی به امنیت و حریم خصوصی شما می‌دهیم. اطلاعاتی که در ربات آترو ذخیره می‌شود، با بالاترین سطح استانداردهای امنیتی محافظت می‌شود. تمامی داده‌ها به‌صورت رمزگذاری‌شده نگهداری می‌شوند و هیچ فرد یا سازمان دیگری به اطلاعات شما دسترسی نخواهد داشت. هدف ما این است که شما با خیال راحت از خدمات ما استفاده کنید و مطمئن باشید که حریم خصوصی شما برای ما در اولویت است.

با تشکر از اعتماد شما  
تیم آترو"""


@app.on_message(filters.command("privacy" ,prefixes=["", "/"]))
async def privacy(client, message: Message):
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("View Privacy Policy", url="https://t.me/pykaliermusicgroup")]]
    )
    await message.reply_text(
        TEXT,
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )
