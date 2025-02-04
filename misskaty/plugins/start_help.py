"""
 * @author        yasir <yasiramunandar@gmail.com>
 * @date          2022-12-01 09:12:27
 * @lastModified  2023-03-30 09:33:16
 * @projectName   MissKatyPyro
 * Copyright @YasirPedia All rights reserved
 """
import re
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery
from database.users_chats_db import db
from pyrogram import filters, Client
from pyrogram.errors import ChannelPrivate
from misskaty import app, BOT_USERNAME, HELPABLE, BOT_NAME
from misskaty.vars import COMMAND_HANDLER, LOG_CHANNEL
from misskaty.core.decorator.ratelimiter import ratelimiter
from misskaty.helper import bot_sys_stats, paginate_modules
from misskaty.helper.localization import use_chat_lang


home_keyboard_pm = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="Commands ❓", callback_data="bot_commands"),
            InlineKeyboardButton(
                text="Source Code 🛠",
                url="https://github.com/yasirarism/MissKatyPyro",
            ),
        ],
        [
            InlineKeyboardButton(
                text="System Stats 🖥",
                callback_data="stats_callback",
            ),
            InlineKeyboardButton(text="Dev 👨", url="https://t.me/YasirArisM"),
        ],
        [
            InlineKeyboardButton(
                text="Add Me To Your Group 🎉",
                url=f"http://t.me/{BOT_USERNAME}?startgroup=new",
            )
        ],
    ]
)

home_text_pm = f"Hey there! My name is {BOT_NAME}. I have many useful features for you, feel free to add me to your group.\n\nIf you want give coffee to my owner you can send /donate command for more info."

keyboard = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton(text="Help ❓", url=f"t.me/{BOT_USERNAME}?start=help"),
            InlineKeyboardButton(
                text="Source Code �",
                url="https://github.com/yasirarism/MissKatyPyro",
            ),
        ],
        [
            InlineKeyboardButton(
                text="System Stats 💻",
                callback_data="stats_callback",
            ),
            InlineKeyboardButton(text="Dev 👨", url="https://t.me/YasirArisM"),
        ],
    ]
)


@app.on_message(filters.command("start", COMMAND_HANDLER))
@use_chat_lang()
async def start(self: Client, ctx: Message, strings):
    if ctx.chat.type.value != "private":
        if not await db.get_chat(ctx.chat.id):
            try:
                total = await app.get_chat_members_count(ctx.chat.id)
            except ChannelPrivate:
                return await ctx.chat.leave()
            await app.send_message(
                LOG_CHANNEL,
                strings("newgroup_log").format(jdl=ctx.chat.title, id=ctx.chat.id, c=total),
            )

            await db.add_chat(ctx.chat.id, ctx.chat.title)
        nama = ctx.from_user.mention if ctx.from_user else ctx.sender_chat.title
        return await ctx.reply_photo(
            photo="https://telegra.ph/file/90e9a448bc2f8b055b762.jpg",
            caption=strings("start_msg").format(kamuh=nama),
            reply_markup=keyboard,
        )
    if not await db.is_user_exist(ctx.from_user.id):
        await db.add_user(ctx.from_user.id, ctx.from_user.first_name)
        await app.send_message(
            LOG_CHANNEL,
            strings("newuser_log").format(id=ctx.from_user.id, nm=ctx.from_user.mention),
        )

    if len(ctx.text.split()) > 1:
        name = (ctx.text.split(None, 1)[1]).lower()
        if "_" in name:
            module = name.split("_", 1)[1]
            text = strings("help_name").format(mod=HELPABLE[module].__MODULE__) + HELPABLE[module].__HELP__
            await ctx.reply_msg(text, disable_web_page_preview=True)
        elif name == "help":
            text, keyb = await help_parser(ctx.from_user.first_name)
            await ctx.reply_msg(
                text,
                reply_markup=keyb,
            )
    else:
        await ctx.reply_photo(
            photo="https://telegra.ph/file/90e9a448bc2f8b055b762.jpg",
            caption=home_text_pm,
            reply_markup=home_keyboard_pm,
        )


@app.on_callback_query(filters.regex("bot_commands"))
@ratelimiter
async def commands_callbacc(self: Client, CallbackQuery: CallbackQuery):
    text, keyboard = await help_parser(CallbackQuery.from_user.mention)
    await app.send_message(
        CallbackQuery.message.chat.id,
        text=text,
        reply_markup=keyboard,
    )
    await CallbackQuery.message.delete_msg()


@app.on_callback_query(filters.regex("stats_callback"))
@ratelimiter
async def stats_callbacc(self: Client, cb: CallbackQuery):
    text = await bot_sys_stats()
    await app.answer_callback_query(cb.id, text, show_alert=True)


@app.on_message(filters.command("help", COMMAND_HANDLER))
@ratelimiter
@use_chat_lang()
async def help_command(self: Client, ctx: Message, strings):
    if ctx.chat.type.value != "private":
        if not await db.get_chat(ctx.chat.id):
            total = await app.get_chat_members_count(ctx.chat.id)
            await app.send_message(
                LOG_CHANNEL,
                strings("newgroup_log").format(jdl=ctx.chat.title, id=ctx.chat.id, c=total),
            )

            await db.add_chat(ctx.chat.id, ctx.chat.title)
        if len(ctx.command) >= 2:
            name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                key = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                text=strings("click_me"),
                                url=f"t.me/{BOT_USERNAME}?start=help_{name}",
                            )
                        ],
                    ]
                )
                await ctx.reply_msg(
                    strings("click_btn"),
                    reply_markup=key,
                )
            else:
                await ctx.reply_msg(strings("pm_detail"), reply_markup=keyboard)
        else:
            await ctx.reply_msg(strings("pm_detail"), reply_markup=keyboard)
    else:
        if not await db.is_user_exist(ctx.from_user.id):
            await db.add_user(ctx.from_user.id, ctx.from_user.first_name)
            await app.send_message(
                LOG_CHANNEL,
                strings("newuser_log").format(id=ctx.from_user.id, nm=ctx.from_user.mention),
            )

        if len(ctx.command) >= 2:
            name = (ctx.text.split(None, 1)[1]).replace(" ", "_").lower()
            if str(name) in HELPABLE:
                text = strings("help_name").format(mod=HELPABLE[name].__MODULE__) + HELPABLE[name].__HELP__
                await ctx.reply_msg(text, disable_web_page_preview=True)
            else:
                text, help_keyboard = await help_parser(ctx.from_user.first_name)
                await ctx.reply_msg(
                    text,
                    reply_markup=help_keyboard,
                    disable_web_page_preview=True,
                )
        else:
            text, help_keyboard = await help_parser(ctx.from_user.first_name)
            await ctx.reply_msg(text, reply_markup=help_keyboard, disable_web_page_preview=True)


async def help_parser(name, keyboard=None):
    if not keyboard:
        keyboard = InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help"))
    return (
        """Hello {first_name}, My name is {bot_name}.
I'm a bot with some useful features. You can change language bot using /setlang command, but it's still in beta stage.
You can choose an option below, by clicking a button.

If you want give coffee to my owner you can send /donate command for more info.
""".format(
            first_name=name,
            bot_name="MissKaty",
        ),
        keyboard,
    )


@app.on_callback_query(filters.regex(r"help_(.*?)"))
@ratelimiter
@use_chat_lang()
async def help_button(self: Client, query: CallbackQuery, strings):
    home_match = re.match(r"help_home\((.+?)\)", query.data)
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data)
    create_match = re.match(r"help_create", query.data)
    top_text = strings("help_txt").format(kamuh=query.from_user.first_name, bot=self.me.first_name)
    if mod_match:
        module = mod_match[1].replace(" ", "_")
        text = strings("help_name").format(mod=HELPABLE[module].__MODULE__) + HELPABLE[module].__HELP__

        await query.message.edit_msg(
            text=text,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(strings("back_btn"), callback_data="help_back")]]),
            disable_web_page_preview=True,
        )
    elif home_match:
        await app.send_msg(
            query.from_user.id,
            text=home_text_pm,
            reply_markup=home_keyboard_pm,
        )
        await query.message.delete_msg()
    elif prev_match:
        curr_page = int(prev_match[1])
        await query.message.edit_msg(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page - 1, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif next_match:
        next_page = int(next_match[1])
        await query.message.edit_msg(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(next_page + 1, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif back_match:
        await query.message.edit_msg(
            text=top_text,
            reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELPABLE, "help")),
            disable_web_page_preview=True,
        )

    elif create_match:
        text, keyboard = await help_parser(query)
        await query.message.edit_msg(
            text=text,
            reply_markup=keyboard,
            disable_web_page_preview=True,
        )

    await self.answer_callback_query(query.id)
