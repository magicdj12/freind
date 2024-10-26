import asyncio
import platform
from sys import version as pyver

import psutil
from ntgcalls import __version__ as ngtgver
from pyrogram import __version__ as pyrover
from pyrogram import filters
from pyrogram.errors import FloodWait, MessageIdInvalid
from pyrogram.types import CallbackQuery, InputMediaPhoto, Message
from pytgcalls.__version__ import __version__ as pytgver

import config
from config import BANNED_USERS
from strings import get_command
from YukkiMusic import YouTube, app
from YukkiMusic.core.userbot import assistants
from YukkiMusic.misc import SUDOERS, pymongodb
from YukkiMusic.plugins import ALL_MODULES
from YukkiMusic.utils.database import (
    get_global_tops,
    get_particulars,
    get_queries,
    get_served_chats,
    get_served_users,
    get_sudoers,
    get_top_chats,
    get_topp_users,
)
from YukkiMusic.utils.decorators.language import language, languageCB
from YukkiMusic.utils.inline.stats import (
    back_stats_buttons,
    back_stats_markup,
    get_stats_markup,
    overallback_stats_markup,
    stats_buttons,
    top_ten_stats_markup,
)

loop = asyncio.get_running_loop()

# Commands
GSTATS_COMMAND = get_command("GSTATS_COMMAND")
STATS_COMMAND = get_command("STATS_COMMAND")


@app.on_message(filters.command(STATS_COMMAND , prefixes=["", "/"]) & ~BANNED_USERS)
@language
async def stats_global(client, message: Message, _):
    upl = stats_buttons(_, True if message.from_user.id in SUDOERS else False)
    await message.reply_photo(
        photo=config.STATS_IMG_URL,
        caption=_["gstats_11"].format(app.mention),
        reply_markup=upl,
    )


@app.on_message(filters.command(GSTATS_COMMAND , prefixes=["", "/"]) & ~BANNED_USERS)
@language
async def gstats_global(client, message: Message, _):
    mystic = await message.reply_text(_["gstats_1"])
    stats = await get_global_tops()
    if not stats:
        await asyncio.sleep(1)
        return await mystic.edit(_["gstats_2"])

    def get_stats():
        results = {}
        for i in stats:
            top_list = stats[i]["spot"]
            results[str(i)] = top_list
            list_arranged = dict(
                sorted(
                    results.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )
        if not results:
            return mystic.edit(_["gstats_2"])
        videoid = None
        co = None
        for vidid, count in list_arranged.items():
            if vidid == "telegram":
                continue
            else:
                videoid = vidid
                co = count
            break
        return videoid, co

    try:
        videoid, co = await loop.run_in_executor(None, get_stats)
    except Exception as e:
        print(e)
        return
    (
        title,
        duration_min,
        duration_sec,
        thumbnail,
        vidid,
    ) = await YouTube.details(videoid, True)
    title = title.title()
    final = f"بیشترین موزیک های پخش شده{app.mention}\n\n**عنوان:** {title}\n\nپخش شده** {co} **زمان"
    upl = get_stats_markup(_, True if message.from_user.id in SUDOERS else False)
    try:
        await app.send_photo(
            message.chat.id,
            photo=thumbnail,
            caption=final,
            reply_markup=upl,
        )
    except FloodWait as e:
        asyncio.sleep(e.value)
    await mystic.delete()


@app.on_callback_query(filters.regex("GetStatsNow") & ~BANNED_USERS)
@languageCB
async def top_users_ten(client, CallbackQuery: CallbackQuery, _):
    chat_id = CallbackQuery.message.chat.id
    callback_data = CallbackQuery.data.strip()
    what = callback_data.split(None, 1)[1]
    upl = back_stats_markup(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    mystic = await CallbackQuery.edit_message_text(
        _["gstats_3"].format(
            f"ᴏғ {CallbackQuery.message.chat.title}" if what == "Here" else what
        )
    )
    if what == "Tracks":
        stats = await get_global_tops()
    elif what == "Chats":
        stats = await get_top_chats()
    elif what == "Users":
        stats = await get_topp_users()
    elif what == "Here":
        stats = await get_particulars(chat_id)
    if not stats:
        await asyncio.sleep(1)
        return await mystic.edit(_["gstats_2"], reply_markup=upl)
    queries = await get_queries()

    def get_stats():
        results = {}
        for i in stats:
            top_list = stats[i] if what in ["Chats", "Users"] else stats[i]["spot"]
            results[str(i)] = top_list
            list_arranged = dict(
                sorted(
                    results.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )
            )
        if not results:
            return mystic.edit(_["gstats_2"], reply_markup=upl)
        msg = ""
        limit = 0
        total_count = 0
        if what in ["Tracks", "Here"]:
            for items, count in list_arranged.items():
                total_count += count
                if limit == 10:
                    continue
                limit += 1
                details = stats.get(items)
                title = (details["title"][:35]).title()
                if items == "telegram":
                    msg += f"🔗[فایل ها و صدای های تلگرام](https://t.me/telegram) ** پخش شده {count} زمان**\n\n"
                else:
                    msg += f"🔗 [{title}](https://www.youtube.com/watch?v={items}) ** پخش شده {count} زمان**\n\n"

            temp = (
                _["gstats_4"].format(
                    queries,
                    app.mention,
                    len(stats),
                    total_count,
                    limit,
                )
                if what == "Tracks"
                else _["gstats_7"].format(len(stats), total_count, limit)
            )
            msg = temp + msg
        return msg, list_arranged

    try:
        msg, list_arranged = await loop.run_in_executor(None, get_stats)
    except Exception as e:
        print(e)
        return
    limit = 0
    if what in ["Users", "Chats"]:
        for items, count in list_arranged.items():
            if limit == 10:
                break
            try:
                extract = (
                    (await app.get_users(items)).first_name
                    if what == "Users"
                    else (await app.get_chat(items)).title
                )
                if extract is None:
                    continue
                await asyncio.sleep(0.5)
            except:
                continue
            limit += 1
            msg += f"🔗`{extract}` پخش شده {count} زمان در ربات.\n\n"
        temp = (
            _["gstats_5"].format(limit, app.mention)
            if what == "Chats"
            else _["gstats_6"].format(limit, app.mention)
        )
        msg = temp + msg
    med = InputMediaPhoto(media=config.GLOBAL_IMG_URL, caption=msg)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.GLOBAL_IMG_URL, caption=msg, reply_markup=upl
        )


@app.on_callback_query(filters.regex("TopOverall") & ~BANNED_USERS)
@languageCB
async def overall_stats(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    what = callback_data.split(None, 1)[1]
    if what != "s":
        upl = overallback_stats_markup(_)
    else:
        upl = back_stats_buttons(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await CallbackQuery.edit_message_text(_["gstats_8"])
    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(SUDOERS)
    mod = len(ALL_MODULES)
    assistant = len(assistants)
    playlist_limit = config.SERVER_PLAYLIST_LIMIT
    fetch_playlist = config.PLAYLIST_FETCH_LIMIT
    song = config.SONG_DOWNLOAD_DURATION
    play_duration = config.DURATION_LIMIT_MIN
    if config.AUTO_LEAVING_ASSISTANT == str(True):
        ass = "Yes"
    else:
        ass = "No"
    text = f"""****آمار و اطلاعات ربات:**

**ماژول‌های وارد شده:** {mod}  
**چت‌های سرویس شده:** {served_chats}  
**کاربران سرویس شده:** {served_users}  
**کاربران مسدود شده:** {blocked}  
**کاربران سودو:** {sudoers}  

**کل درخواست‌ها:** {total_queries}  
**تعداد دستیارها:** {assistant}  
**دستیار خروج خودکار:** {ass}  

**محدودیت مدت زمان پخش:** {play_duration} دقیقه  
**محدودیت دانلود آهنگ:** {song} دقیقه  
**محدودیت لیست پخش سرور ربات:** {playlist_limit}  
**محدودیت پخش لیست پخش:** {fetch_playlist}
"""
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )


@app.on_callback_query(filters.regex("bot_stats_sudo"))
@languageCB
async def overall_stats(client, CallbackQuery, _):
    if CallbackQuery.from_user.id not in SUDOERS:
        return await CallbackQuery.answer("فقط برای کاربران سودو", show_alert=True)
    callback_data = CallbackQuery.data.strip()
    what = callback_data.split(None, 1)[1]
    if what != "s":
        upl = overallback_stats_markup(_)
    else:
        upl = back_stats_buttons(_)
    try:
        await CallbackQuery.answer()
    except:
        pass
    await CallbackQuery.edit_message_text(_["gstats_8"])
    sc = platform.system()
    p_core = psutil.cpu_count(logical=False)
    t_core = psutil.cpu_count(logical=True)
    ram = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
    try:
        cpu_freq = psutil.cpu_freq().current
        if cpu_freq >= 1000:
            cpu_freq = f"{round(cpu_freq / 1000, 2)}GHz"
        else:
            cpu_freq = f"{round(cpu_freq, 2)}MHz"
    except:
        cpu_freq = "Unable to Fetch"
    hdd = psutil.disk_usage("/")
    total = hdd.total / (1024.0**3)
    total = str(total)
    used = hdd.used / (1024.0**3)
    used = str(used)
    free = hdd.free / (1024.0**3)
    free = str(free)
    mod = len(ALL_MODULES)
    db = pymongodb
    call = db.command("dbstats")
    datasize = call["dataSize"] / 1024
    datasize = str(datasize)
    storage = call["storageSize"] / 1024
    objects = call["objects"]
    collections = call["collections"]

    served_chats = len(await get_served_chats())
    served_users = len(await get_served_users())
    total_queries = await get_queries()
    blocked = len(BANNED_USERS)
    sudoers = len(await get_sudoers())
    text = f""" **آمار و اطلاعات ربات:**

**ماژول‌های وارد شده:** {mod}  
**پلتفرم:** {sc}  
**رم:** {ram}  
**هسته‌های فیزیکی:** {p_core}  
**کل هسته‌ها:** {t_core}  
**فرکانس CPU:** {cpu_freq}  

**نسخه پایتون :** {pyver.split()[0]}  
**نسخه پایروگرام :** {pyrover}  
**نسخه Py-TgCalls :** {pytgver}  
**نسخه N-TgCalls :** {ngtgver}  
**فضای ذخیره‌سازی موجود :** {total[:4]} گیگابایت  
**فضای ذخیره‌سازی استفاده شده :** {used[:4]} گیگابایت  
**فضای ذخیره‌سازی باقی‌مانده :** {free[:4]} گیگابایت  

**چت‌های سرویس شده:** {served_chats}  
**کاربران سرویس شده:** {served_users}  
**کاربران مسدود شده:** {blocked}  
**کاربران سودو:** {sudoers}  

**کل فضای ذخیره‌سازی دیتابیس:** {storage} مگابایت  
**کل مجموعه‌های دیتابیس:** {collections}  
**کل کلیدهای دیتابیس:** {objects}  
**کل درخواست‌های ربات:** `{total_queries}`  
"""
    med = InputMediaPhoto(media=config.STATS_IMG_URL, caption=text)
    try:
        await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
    except MessageIdInvalid:
        await CallbackQuery.message.reply_photo(
            photo=config.STATS_IMG_URL, caption=text, reply_markup=upl
        )


@app.on_callback_query(
    filters.regex(pattern=r"^(TOPMARKUPGET|GETSTATS|GlobalStats)$") & ~BANNED_USERS
)
@languageCB
async def back_buttons(client, CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    command = CallbackQuery.matches[0].group(1)
    if command == "TOPMARKUPGET":
        upl = top_ten_stats_markup(_)
        med = InputMediaPhoto(
            media=config.GLOBAL_IMG_URL,
            caption=_["gstats_9"],
        )
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.GLOBAL_IMG_URL,
                caption=_["gstats_9"],
                reply_markup=upl,
            )
    if command == "GlobalStats":
        upl = get_stats_markup(
            _,
            True if CallbackQuery.from_user.id in SUDOERS else False,
        )
        med = InputMediaPhoto(
            media=config.GLOBAL_IMG_URL,
            caption=_["gstats_10"].format(app.mention),
        )
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.GLOBAL_IMG_URL,
                caption=_["gstats_10"].format(app.mention),
                reply_markup=upl,
            )
    if command == "GETSTATS":
        upl = stats_buttons(
            _,
            True if CallbackQuery.from_user.id in SUDOERS else False,
        )
        med = InputMediaPhoto(
            media=config.STATS_IMG_URL,
            caption=_["gstats_11"].format(app.mention),
        )
        try:
            await CallbackQuery.edit_message_media(media=med, reply_markup=upl)
        except MessageIdInvalid:
            await CallbackQuery.message.reply_photo(
                photo=config.STATS_IMG_URL,
                caption=_["gstats_11"].format(app.mention),
                reply_markup=upl,
            )
