import os
import shutil

from pyrogram import filters

from YukkiMusic import app
from YukkiMusic.misc import SUDOERS


@app.on_message(filters.command("clean" , prefixes=["", "/"]) & SUDOERS)
async def clean(_, message):
    A = await message.reply_text("حذف پوشه ها ...")
    dir = "downloads"
    dir1 = "cache"
    shutil.rmtree(dir)
    shutil.rmtree(dir1)
    os.mkdir(dir)
    os.mkdir(dir1)
    await A.edit("اطلاعات پوشه های خالی شد ")
