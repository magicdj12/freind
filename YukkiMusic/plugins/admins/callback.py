import random

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup

from config import (
    BANNED_USERS,
    SOUNCLOUD_IMG_URL,
    STREAM_IMG_URL,
    SUPPORT_GROUP,
    TELEGRAM_AUDIO_URL,
    TELEGRAM_VIDEO_URL,
    adminlist,
)
from YukkiMusic import YouTube, app
from YukkiMusic.core.call import Yukki
from YukkiMusic.misc import SUDOERS, db
from YukkiMusic.utils.database import (
    is_active_chat,
    is_music_playing,
    is_muted,
    is_nonadmin_chat,
    music_off,
    music_on,
    mute_off,
    mute_on,
    set_loop,
)
from YukkiMusic.utils.decorators.language import languageCB
from YukkiMusic.utils.formatters import seconds_to_min
from YukkiMusic.utils.inline.play import stream_markup, telegram_markup
from YukkiMusic.utils.stream.autoclear import auto_clean
from YukkiMusic.utils.thumbnails import gen_thumb

wrong = {}
downvote = {}
downvoters = {}


@app.on_callback_query(filters.regex("ADMIN")  & ~BANNED_USERS)
@languageCB
async def del_back_playlist(client, CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    command, chat = callback_request.split("|")
    chat_id = int(chat)
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_6"], show_alert=True)
    mention = CallbackQuery.from_user.mention
    is_non_admin = await is_nonadmin_chat(CallbackQuery.message.chat.id)
    if not is_non_admin:
        if CallbackQuery.from_user.id not in SUDOERS:
            admins = adminlist.get(CallbackQuery.message.chat.id)
            if not admins:
                return await CallbackQuery.answer(_["admin_18"], show_alert=True)
            else:
                if CallbackQuery.from_user.id not in admins:
                    return await CallbackQuery.answer(_["admin_19"], show_alert=True)
    if command == "Pause" or command == "توقف":
        if not await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_1"], show_alert=True)
        await CallbackQuery.answer()
        await music_off(chat_id)
        await Yukki.pause_stream(chat_id)
        await CallbackQuery.message.reply_text(
            _["admin_2"].format(mention), disable_web_page_preview=True
        )
    elif command == "Resume" or command == "ادامه":
        if await is_music_playing(chat_id):
            return await CallbackQuery.answer(_["admin_3"], show_alert=True)
        await CallbackQuery.answer()
        await music_on(chat_id)
        await Yukki.resume_stream(chat_id)
        await CallbackQuery.message.reply_text(
            _["admin_4"].format(mention), disable_web_page_preview=True
        )
    elif command == "Stop" or command == "End" or command == "ختم" or command == "اتمام":
        await CallbackQuery.answer()
        await Yukki.stop_stream(chat_id)
        await set_loop(chat_id, 0)
        await CallbackQuery.message.reply_text(
            _["admin_9"].format(mention), disable_web_page_preview=True
        )
    elif command == "Mute" or command == "بیصدا":
        if await is_muted(chat_id):
            return await CallbackQuery.answer(_["admin_5"], show_alert=True)
        await CallbackQuery.answer()
        await mute_on(chat_id)
        await Yukki.mute_stream(chat_id)
        await CallbackQuery.message.reply_text(
            _["admin_6"].format(mention), disable_web_page_preview=True
        )
    elif command == "Unmute" or command == "باصدا":
        if not await is_muted(chat_id):
            return await CallbackQuery.answer(_["admin_7"], show_alert=True)
        await CallbackQuery.answer()
        await mute_off(chat_id)
        await Yukki.unmute_stream(chat_id)
        await CallbackQuery.message.reply_text(
            _["admin_8"].format(mention), disable_web_page_preview=True
        )
    elif command == "Loop" or command == "تکرار":
        await CallbackQuery.answer()
        await set_loop(chat_id, 3)
        await CallbackQuery.message.reply_text(_["admin_25"].format(mention, 3))

    elif command == "Shuffle" or command == "تصادفی":
        check = db.get(chat_id)
        if not check:
            return await CallbackQuery.answer(_["admin_21"], show_alert=True)
        try:
            popped = check.pop(0)
        except:
            return await CallbackQuery.answer(_["admin_22"], show_alert=True)
        check = db.get(chat_id)
        if not check:
            check.insert(0, popped)
            return await CallbackQuery.answer(_["admin_22"], show_alert=True)
        await CallbackQuery.answer()
        random.shuffle(check)
        check.insert(0, popped)
        await CallbackQuery.message.reply_text(
            _["admin_23"].format(mention), disable_web_page_preview=True
        )

    elif command == "Skip" or command == "بعدی":
        check = db.get(chat_id)
        txt = f"» موزیک رد شد توسط {mention} !"
        popped = None
        try:
            popped = check.pop(0)
            if popped:
                await auto_clean(popped)
            if not check:
                await CallbackQuery.edit_message_text(f"» موزیک رد شد توسط {mention} !")
                await CallbackQuery.message.reply_text(
                    _["admin_10"].format(mention), disable_web_page_preview=True
                )
                try:
                    return await Yukki.stop_stream(chat_id)
                except:
                    return
        except:
            try:
                await CallbackQuery.edit_message_text(f"» موزیک رد شد توسط {mention} !")
                await CallbackQuery.message.reply_text(
                    _["admin_10"].format(mention), disable_web_page_preview=True
                )
                return await Yukki.stop_stream(chat_id)
            except:
                return
        await CallbackQuery.answer()
        queued = check[0]["file"]
        title = (check[0]["title"]).title()
        user = check[0]["by"]
        streamtype = check[0]["streamtype"]
        videoid = check[0]["vidid"]
        duration_min = check[0]["dur"]
        CallbackQuery.message.from_user.id
        status = True if str(streamtype) == "video" else None
        db[chat_id][0]["played"] = 0
        if "live_" in queued:
            n, link = await YouTube.video(videoid, True)
            if n == 0:
                return await CallbackQuery.message.reply_text(
                    _["admin_11"].format(title)
                )
            try:
                await Yukki.skip_stream(chat_id, link, video=status)
            except Exception:
                return await CallbackQuery.message.reply_text(_["call_7"])
            button = telegram_markup(_, chat_id)
            img = await gen_thumb(videoid)
            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    user,
                    f"https://t.me/{app.username}?start=info_{videoid}",
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await CallbackQuery.edit_message_text(txt)
        elif "vid_" in queued:
            mystic = await CallbackQuery.message.reply_text(
                _["call_8"], disable_web_page_preview=True
            )
            try:
                file_path, direct = await YouTube.download(
                    videoid,
                    mystic,
                    videoid=True,
                    video=status,
                )
            except:
                return await mystic.edit_text(_["call_7"])
            try:
                await Yukki.skip_stream(chat_id, file_path, video=status)
            except Exception:
                return await mystic.edit_text(_["call_7"])
            button = stream_markup(_, videoid, chat_id)
            img = await gen_thumb(videoid)
            run = await CallbackQuery.message.reply_photo(
                photo=img,
                caption=_["stream_1"].format(
                    title[:27],
                    f"https://t.me/{app.username}?start=info_{videoid}",
                    duration_min,
                    user,
                ),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt)
            await mystic.delete()
        elif "index_" in queued:
            try:
                await Yukki.skip_stream(chat_id, videoid, video=status)
            except Exception:
                return await CallbackQuery.message.reply_text(_["call_7"])
            button = telegram_markup(_, chat_id)
            run = await CallbackQuery.message.reply_photo(
                photo=STREAM_IMG_URL,
                caption=_["stream_2"].format(user),
                reply_markup=InlineKeyboardMarkup(button),
            )
            db[chat_id][0]["mystic"] = run
            db[chat_id][0]["markup"] = "tg"
            await CallbackQuery.edit_message_text(txt)
        else:
            try:
                await Yukki.skip_stream(chat_id, queued, video=status)
            except Exception:
                return await CallbackQuery.message.reply_text(_["call_7"])
            if videoid == "telegram":
                button = telegram_markup(_, chat_id)
                run = await CallbackQuery.message.reply_photo(
                    photo=(
                        TELEGRAM_AUDIO_URL
                        if str(streamtype) == "audio"
                        else TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        title, SUPPORT_GROUP, check[0]["dur"], user
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif videoid == "soundcloud":
                button = telegram_markup(_, chat_id)
                run = await CallbackQuery.message.reply_photo(
                    photo=(
                        SOUNCLOUD_IMG_URL
                        if str(streamtype) == "audio"
                        else TELEGRAM_VIDEO_URL
                    ),
                    caption=_["stream_1"].format(
                        title, SUPPORT_GROUP, check[0]["dur"], user
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                button = stream_markup(_, videoid, chat_id)
                img = await gen_thumb(videoid)
                run = await CallbackQuery.message.reply_photo(
                    photo=img,
                    caption=_["stream_1"].format(
                        title[:27],
                        f"https://t.me/{app.username}?start=info_{videoid}",
                        duration_min,
                        user,
                    ),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            await CallbackQuery.edit_message_text(txt)
    else:
        playing = db.get(chat_id)
        if not playing:
            return await CallbackQuery.answer(_["queue_2"], show_alert=True)
        duration_seconds = int(playing[0]["seconds"])
        if duration_seconds == 0:
            return await CallbackQuery.answer(_["admin_30"], show_alert=True)
        file_path = playing[0]["file"]
        if "index_" in file_path or "live_" in file_path:
            return await CallbackQuery.answer(_["admin_30"], show_alert=True)
        duration_played = int(playing[0]["played"])
        if int(command) in [1, 2]:
            duration_to_skip = 10
        else:
            duration_to_skip = 30
        duration = playing[0]["dur"]
        if int(command) in [1, 3]:
            if (duration_played - duration_to_skip) <= 10:
                bet = seconds_to_min(duration_played)
                return await CallbackQuery.answer(
                    f"» ربات نمیتواند به عقب برگرداند بخاطر مدت کم موزیک.\n\nتازه پخش شده  :** {bet}** زمانی باقی مانده **{duration}** دقیقه.",
                    show_alert=True,
                )
            to_seek = duration_played - duration_to_skip + 1
        else:
            if (duration_seconds - (duration_played + duration_to_skip)) <= 10:
                bet = seconds_to_min(duration_played)
                return await CallbackQuery.answer(
                    f"» ربات نمیتواند به عقب برگرداند بخاطر مدت کم موزیک.\n\nتازه پخش شده  :** {bet}** زمانی باقی مانده **{duration}** دقیقه.",
                    show_alert=True,
                )
            to_seek = duration_played + duration_to_skip + 1
        await CallbackQuery.answer()
        mystic = await CallbackQuery.message.reply_text(_["admin_32"])
        if "vid_" in file_path:
            n, file_path = await YouTube.video(playing[0]["vidid"], True)
            if n == 0:
                return await mystic.edit_text(_["admin_30"])
        try:
            await Yukki.seek_stream(
                chat_id,
                file_path,
                seconds_to_min(to_seek),
                duration,
                playing[0]["streamtype"],
            )
        except:
            return await mystic.edit_text(_["admin_34"])
        if int(command) in [1, 3]:
            db[chat_id][0]["played"] -= duration_to_skip
        else:
            db[chat_id][0]["played"] += duration_to_skip
        string = _["admin_33"].format(seconds_to_min(to_seek))
        await mystic.edit_text(f"{string}\n\nᴄʜᴀɴɢᴇs ᴅᴏɴᴇ ʙʏ : {mention} !")


__MODULE__ = "دستورات مدیر"
__HELP__ = """
<b>c نمایانگر پخش کانال است.</b>

<b>✧ /pause /توقف</b> یا <b>/cpause /کانال توقف</b> - پخش موسیقی در حال پخش را متوقف کنید.
<b>✧ /resume /ادامه</b> یا <b>/cresume /کانال ادامه</b> - موسیقی متوقف‌شده را از سر بگیرید.
<b>✧ /mute /بی‌صدا</b> یا <b>/cmute /کانال بی‌صدا</b> - موسیقی در حال پخش را بی‌صدا کنید.
<b>✧ /unmute /صدا</b> یا <b>/cunmute /کانال صدا</b> - موسیقی بی‌صدا شده را دوباره صدا دار کنید.
<b>✧ /skip /رد کردن</b> یا <b>/cskip /کانال رد کردن</b> - موسیقی در حال پخش را رد کنید.
<b>✧ /stop /متوقف کردن</b> یا <b>/cstop /کانال متوقف کردن</b> - موسیقی در حال پخش را متوقف کنید.
<b>✧ /shuffle /تصادفی</b> یا <b>/cshuffle /کانال تصادفی</b> - لیست پخش در حال انتظار را به‌طور تصادفی جابجا کنید.
<b>✧ /seek /جستجو به جلو</b> یا <b>/cseek /کانال جستجو به جلو</b> - موسیقی را به مدت زمان دلخواه جلو ببرید.
<b>✧ /seekback /جستجو به عقب</b> یا <b>/cseekback /کانال جستجو به عقب</b> - موسیقی را به مدت زمان دلخواه به عقب ببرید.
<b>✧ /reboot /راه‌اندازی مجدد</b> - ربات را برای چت شما راه‌اندازی مجدد کنید.

<b>✧ /skip /رد کردن</b> یا <b>/cskip /کانال رد کردن</b> [شماره (مثال: 𝟹)] - موسیقی را به شماره دلخواه در لیست انتظار رد می‌کند. مثال: <b>/skip 𝟹</b> موسیقی را به سومین موسیقی در لیست انتظار رد می‌کند و موسیقی‌های شماره 𝟷 و 𝟸 را نادیده می‌گیرد.

<b>✧ /loop /حلقه</b> یا <b>/cloop /کانال حلقه</b> [فعال/غیرفعال] یا [شماره‌های بین 𝟷-𝟶] - هنگامی که فعال باشد، ربات موسیقی در حال پخش را به تعداد 𝟷-𝟶 بار در چت صوتی تکرار می‌کند. پیش‌فرض به تعداد 𝟷𝟶 بار است.
"""
