
import uvloop

uvloop.install()


import sys

from pyrogram import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)

import config

from ..logging import LOGGER


class YukkiBot(Client):
    def __init__(self):
        LOGGER(__name__).info(f"Starting Bot")
        super().__init__(
            "PyKalier",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
        )

    async def start(self):
        await super().start()
        get_me = await self.get_me()
        self.username = get_me.username
        self.id = get_me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.mention = self.me.mention

        try:
            await self.send_message(
                config.LOG_GROUP_ID,
                text=f"<u><b>{self.mention} ربات شروع به کار کرد :</b><u>\n\nآیدی  : <code>{self.id}</code>\nنام : {self.name}\nنام کاربری  : @{self.username}",
            )
        except:
            LOGGER(__name__).error(
                "ربات نتوانسته به گروه لاگ دسترسی پیدا کند. مطمئن شوید که ربات خود را به کانال لاگ اضافه کرده‌اید و به عنوان مدیر ارتقا داده‌اید!"
            )
            # sys.exit()
        if config.SET_CMDS == str(True):
            try:

                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "شروع ربات"),
                        BotCommand("help", "دستورات کمک"),
                        BotCommand("ping", "چک کردن ربات"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "شروع پخش موزیک"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("play", "شروع پخش موزیک"),
                        BotCommand("skip", "رفتن به موزیک بعدی"),
                        BotCommand("pause", "توقف موزیک در حال پخش"),
                        BotCommand("resume", "ادامه موزیک"),
                        BotCommand("end", "بستن پخش ویس چت"),
                        BotCommand("shuffle", "پخش اتفاقی"),
                        BotCommand(
                            "playmode",
                            "دیدن حالت پخش",
                        ),
                        BotCommand(
                            "settings",
                            "باز کردن تنظیمات ربات برای چت شما.",
                        ),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )
            except:
                pass
        else:
            pass
        try:
            a = await self.get_chat_member(config.LOG_GROUP_ID, self.id)
            if a.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).error("Please promote Bot as Admin in Logger Group")
                sys.exit()
        except Exception:
            pass
        if get_me.last_name:
            self.name = get_me.first_name + " " + get_me.last_name
        else:
            self.name = get_me.first_name
        LOGGER(__name__).info(f"MusicBot Started as {self.name}")
