from pyrogram import filters

from strings import get_command
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database import autoend_off, autoend_on

# Commands
AUTOEND_COMMAND = get_command("AUTOEND_COMMAND")


@app.on_message(filters.command(AUTOEND_COMMAND , prefixes=["", "/"]) & SUDOERS)
async def auto_end_stream(client, message):
    usage = "**ᴜsᴀɢᴇ:**\n\n/autoend [enable|disable]"
    if len(message.command) != 2:
        return await message.reply_text(usage)
    state = message.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await autoend_on()
        await message.reply_text(
            "ختم خودکار فعال شد .\n\nربات بعد از 3 دقیقه ویس چت را ترک میکند هیچ کس به ربات گوش نمیدهد ."
        )
    elif state == "disable":
        await autoend_off()
        await message.reply_text("ختم خودکار غیر فعال شد ")
    else:
        await message.reply_text(usage)
