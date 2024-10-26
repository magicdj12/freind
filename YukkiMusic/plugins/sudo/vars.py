import asyncio

from pyrogram import filters

import config
from strings import get_command
from YukkiMusic import app
from YukkiMusic.misc import SUDOERS
from YukkiMusic.utils.database.memorydatabase import get_video_limit
from YukkiMusic.utils.formatters import convert_bytes

VARS_COMMAND = get_command("VARS_COMMAND")


@app.on_message(filters.command(VARS_COMMAND , prefixes=["", "/"]) & SUDOERS)
async def varsFunc(client, message):
    mystic = await message.reply_text("لطفاً صبر کنید.. در حال دریافت تنظیمات شما")
    v_limit = await get_video_limit()
    up_r = f"[Repo]({config.UPSTREAM_REPO})"
    up_b = config.UPSTREAM_BRANCH
    auto_leave = config.AUTO_LEAVE_ASSISTANT_TIME
    yt_sleep = config.YOUTUBE_DOWNLOAD_EDIT_SLEEP
    tg_sleep = config.TELEGRAM_DOWNLOAD_EDIT_SLEEP
    playlist_limit = config.SERVER_PLAYLIST_LIMIT
    fetch_playlist = config.PLAYLIST_FETCH_LIMIT
    song = config.SONG_DOWNLOAD_DURATION
    play_duration = config.DURATION_LIMIT_MIN
    if config.AUTO_LEAVING_ASSISTANT == str(True):
        ass = "Yes"
    else:
        ass = "No"
    if config.PRIVATE_BOT_MODE == str(True):
        pvt = "Yes"
    else:
        pvt = "No"
    if not config.GITHUB_REPO:
        git = "No"
    else:
        git = f"[Repo]({config.GITHUB_REPO})"
    if not config.START_IMG_URL:
        start = "No"
    else:
        start = f"[Image]({config.START_IMG_URL})"
    if not config.SUPPORT_CHANNEL:
        s_c = "No"
    else:
        s_c = f"[Channel]({config.SUPPORT_CHANNEL})"
    if not config.SUPPORT_GROUP:
        s_g = "No"
    else:
        s_g = f"[Group]({config.SUPPORT_GROUP})"
    if not config.GIT_TOKEN:
        token = "No"
    else:
        token = "Yes"
    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        sotify = "No"
    else:
        sotify = "Yes"
    owners = [str(ids) for ids in config.OWNER_ID]
    owner_id = " ,".join(owners)
    tg_aud = convert_bytes(config.TG_AUDIO_FILESIZE_LIMIT)
    tg_vid = convert_bytes(config.TG_VIDEO_FILESIZE_LIMIT)
    text = f"""**MUSIC BOT CONFIG:**

<u>متغیرهای پایه:</u>
مدت_محدودیت : {play_duration} دقیقه  
مدت_محدودیت_دانلود_ترانه : {song} دقیقه  
شناسه_مالک : {owner_id}  

<u>متغیرهای مخزن سفارشی:</u>
مخزن_بالا : {up_r}  
شاخه_بالا : {up_b}  
مخزن_گیت : {git}  
توکن : {token}  

<u>متغیرهای ربات:</u>
کمک_خودکار : {ass}  
زمان_ترک_خودکار : {auto_leave} ثانیه  
حالت_خصوصی : {pvt}  
خواب_ویرایش_یوتیوب : {yt_sleep} ثانیه  
خواب_ویرایش_تلگرام : {tg_sleep} ثانیه  
محدودیت_جریان_ویدئو : {v_limit} چت  
محدودیت_پلی‌لیست_سرور : {playlist_limit}  
محدودیت_دریافت_پلی‌لیست : {fetch_playlist}  

<u>متغیرهای اسپاتیفای:</u>
شناسه_کلاینت_اسپاتیفای : {sotify}  
رمز_کلاینت_اسپاتیفای : {sotify}  

<u>متغیرهای Playsize:</u>
محدودیت_حجم_صوتی_TG : {tg_aud}  
محدودیت_حجم_ویدیویی_TG : {tg_vid}  

<u>متغیرهای URL:</u>
کانال_پشتیبانی : {s_c}  
گروه_پشتیبانی : {s_g}  
آدرس_IMG_شروع : {start}
    """
    await asyncio.sleep(1)

    await mystic.edit_text(text)
