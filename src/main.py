"""Main application script"""

import asyncio
from functools import wraps
from os import getpid
from time import time
from typing import Iterable

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramForbiddenError
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand, Message

from constants import (
    COMMAND_ADDUSER,
    COMMAND_CANCEL,
    COMMAND_CHECK,
    COMMAND_DELUSER,
    COMMAND_GETUSERS,
    COMMAND_HELP,
    COMMAND_ID,
    DOWNTIME_NOTIFICATION_TIMEOUT,
    MIN_DOWNTIME,
    ROLE_ADMIN,
    ROLE_USER,
)
from db import IMSADB
from env_vars import BOT_TOKEN
from helpers import (
    format_seconds,
    get_uptime,
    is_valid_string,
    render_template,
    wait_for_network,
)
from log import log_userinfo, logger
from network_tracker import start_network_tracker
from timer import get_downtime, start_timer

# Bot dispatcher
dp = Dispatcher()

# Database
db = IMSADB()

# Bot start time
bot_start_time: float = time()


class AddUserSession(StatesGroup):
    """Class to handle states of adduser command"""

    adduser_telegram_id = State()
    adduser_name = State()
    adduser_role = State()


class DelUserSession(StatesGroup):
    """Class to handle states of deluser command"""

    deluser_telegram_id = State()


def skip_downtime(func):
    """Decorator to skip messages during downtime."""

    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.date.timestamp() < bot_start_time:
            return
        return await func(message, *args, **kwargs)

    return wrapper


def require_user(func):
    """Decorator to check if message has valid user object."""

    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user is None:
            logger.error("Can not get user info from message: %d", message.message_id)
            return
        return await func(message, *args, **kwargs)

    return wrapper


def only_for_registered(handler):
    """Decorator to only allow whitelisted users to send requests"""

    @require_user
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        assert message.from_user is not None
        if await db.is_user(message.from_user.id) is False:
            logger.debug(
                "Access denied for not registered user. %s", log_userinfo(message)
            )
            return
        return await handler(message, *args, **kwargs)

    return wrapper


def only_for_admin(handler):
    """Decorator to only allow admin to send requests"""

    @require_user
    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        assert message.from_user is not None
        if await db.is_admin(message.from_user.id) is False:
            logger.debug("Admin access denied. %s", log_userinfo(message))
            return
        return await handler(message, *args, **kwargs)

    return wrapper


@dp.message(Command(COMMAND_CANCEL))
@skip_downtime
@only_for_admin
async def command_cancel(message: Message, state: FSMContext):
    """Handler to cancel state"""
    logger.debug("Canceling state. %s", log_userinfo(message))
    await state.clear()
    await message.answer(render_template("cancel.html"))


@dp.message(Command(COMMAND_ID))
@skip_downtime
async def command_id_handler(message: Message) -> None:
    """This handler receives messages with 'id' command"""
    assert message.from_user is not None

    logger.debug("Sending user ID. %s", log_userinfo(message))
    await message.answer(render_template("id.html", user_id=message.from_user.id))


@dp.message(CommandStart())
@skip_downtime
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with 'start' command"""
    assert message.from_user is not None

    # Greet user
    logger.debug("Sending greeting. %s", log_userinfo(message))
    await message.answer(
        render_template("greeting.html", username=message.from_user.username),
        disable_web_page_preview=True,
    )

    # Invoke bot help
    await command_help_handler(message)


@dp.message(Command(COMMAND_HELP))
@skip_downtime
async def command_help_handler(message: Message) -> None:
    """This handler receives messages with 'help' command"""
    assert message.from_user is not None
    logger.debug("Sending help message. %s", log_userinfo(message))

    if await db.is_admin(message.from_user.id):
        await message.answer(
            render_template(
                "help_admin.html",
                cmd_start=CommandStart().commands[0],
                cmd_help=COMMAND_HELP,
                cmd_id=COMMAND_ID,
                cmd_check=COMMAND_CHECK,
                cmd_adduser=COMMAND_ADDUSER,
                cmd_cancel=COMMAND_CANCEL,
                cmd_getusers=COMMAND_GETUSERS,
                cmd_deluser=COMMAND_DELUSER,
            )
        )
    elif await db.is_user(message.from_user.id):
        await message.answer(
            render_template(
                "help_user.html",
                cmd_start=CommandStart().commands[0],
                cmd_help=COMMAND_HELP,
                cmd_id=COMMAND_ID,
                cmd_check=COMMAND_CHECK,
                cmd_cancel=COMMAND_CANCEL,
            )
        )
    else:
        await message.answer(
            render_template(
                "help_unauthorized.html",
                cmd_start=CommandStart().commands[0],
                cmd_help=COMMAND_HELP,
                cmd_id=COMMAND_ID,
            )
        )


@dp.message(Command(COMMAND_CHECK))
@skip_downtime
@only_for_registered
async def command_check_handler(message: Message) -> None:
    """This handler receives messages with 'check' command"""
    assert message.from_user is not None
    logger.debug("Sending check. %s", log_userinfo(message))

    # Get server uptime
    uptime = await get_uptime()
    if uptime is None:
        await message.answer(
            render_template("error.html", details="Failed to get server uptime")
        )
        return
    await message.answer(render_template("check.html", uptime=uptime))


@dp.message(Command(COMMAND_GETUSERS))
@skip_downtime
@only_for_admin
async def command_getusers_handler(message: Message) -> None:
    """This handler receives messages with 'get_users' command"""
    assert message.from_user is not None
    logger.debug("Handling getusers. %s", log_userinfo(message))

    # Get all users
    users = await db.get_all_users()
    if users is False:
        render_template("error.html", details="Failed to get users data")
        return

    # Send all users
    await message.answer(render_template("getusers.html", users=users))


@dp.message(Command(COMMAND_DELUSER))
@skip_downtime
@only_for_admin
async def command_deluser_handler(message: Message, state: FSMContext) -> None:
    """This handler receives messages with 'delete_user' command"""
    assert message.from_user is not None
    logger.debug("Handling deluser. %s", log_userinfo(message))

    # Ask for target user Telegram ID
    await message.answer(render_template("deluser_telegram_id.html"))
    await state.set_state(DelUserSession.deluser_telegram_id)


@dp.message(DelUserSession.deluser_telegram_id)
@skip_downtime
@only_for_admin
async def command_deluser_telegram_id_handler(message: Message, state: FSMContext):
    """This handler receives telegram_id with 'delete_user' command"""
    assert message.from_user is not None
    logger.debug("Handling deluser telegram_id. %s", log_userinfo(message))

    # Get Telegram ID
    try:
        telegram_id = int(str(message.text))
    except ValueError:
        await message.answer(
            render_template("error.html", details="Incorrect Telegram ID")
        )
        await command_cancel(message, state)
        return
    logger.debug(
        "Got Telegram ID to delete user: %d. %s", telegram_id, log_userinfo(message)
    )

    # Delete user
    result = await db.delete_user(telegram_id)
    if result is False:
        await message.answer(
            render_template("error.html", details="Failed to delete user")
        )
        await command_cancel(message, state)
        return

    # Final message
    await message.answer(render_template("deluser_final.html"))


@dp.message(Command(COMMAND_ADDUSER))
@skip_downtime
@only_for_admin
async def command_adduser_handler(message: Message, state: FSMContext) -> None:
    """This handler receives messages with 'add_user' command"""
    assert message.from_user is not None
    logger.debug("Handling adduser. %s", log_userinfo(message))

    # Ask for new user name
    await message.answer(render_template("adduser_name.html"))
    await state.set_state(AddUserSession.adduser_name)


@dp.message(AddUserSession.adduser_name)
@skip_downtime
@only_for_admin
async def command_adduser_name_handler(message: Message, state: FSMContext):
    """This handler receives telegnameram_id with 'add_user' command"""
    assert message.from_user is not None
    logger.debug("Handling adduser name. %s", log_userinfo(message))

    # Get Name
    name = str(message.text)
    if not is_valid_string(name):
        await message.answer(
            render_template(
                "error.html",
                details="Incorrect name. Only lowercase, uppercase, number and underscore allowed",
            )
        )
        await command_cancel(message, state)
        return
    logger.debug("Got name for new user: %s. %s", name, log_userinfo(message))

    # Set Telegram ID
    await state.update_data(name=name)

    # Ask for new user Telegram ID
    await message.answer(render_template("adduser_telegram_id.html"))
    await state.set_state(AddUserSession.adduser_telegram_id)


@dp.message(AddUserSession.adduser_telegram_id)
@skip_downtime
@only_for_admin
async def command_adduser_telegram_id_handler(message: Message, state: FSMContext):
    """This handler receives telegram_id with 'add_user' command"""
    assert message.from_user is not None
    logger.debug("Handling adduser telegram_id. %s", log_userinfo(message))

    # Get Telegram ID
    try:
        telegram_id = int(str(message.text))
    except ValueError:
        await message.answer(
            render_template("error.html", details="Incorrect Telegram ID")
        )
        await command_cancel(message, state)
        return
    logger.debug(
        "Got Telegram ID for new user: %d. %s", telegram_id, log_userinfo(message)
    )

    # Set Telegram ID
    await state.update_data(telegram_id=telegram_id)

    # Ask for new user role
    await message.answer(
        render_template("adduser_role.html", roles=(ROLE_USER, ROLE_ADMIN))
    )
    await state.set_state(AddUserSession.adduser_role)


@dp.message(AddUserSession.adduser_role)
@skip_downtime
@only_for_admin
async def command_adduser_role_handler(message: Message, state: FSMContext):
    """This handler receives role with 'add_user' command"""
    assert message.from_user is not None
    logger.debug("Handling adduser role. %s", log_userinfo(message))

    # Get role
    role = str(message.text)
    if role not in (ROLE_ADMIN, ROLE_USER):
        await message.answer(render_template("error.html", details="Incorrect role"))
        await command_cancel(message, state)
        return
    logger.debug("Got role for new user: %s. %s", role, log_userinfo(message))

    # Get session data
    state_data = await state.get_data()

    # Get Telegram ID
    telegram_id = int(str(state_data.get("telegram_id")))  # Validated before

    # Get Name
    name = str(state_data.get("name"))  # Validated before

    # Create new user
    await db.add_user(telegram_id, name, role)

    # Final message
    await message.answer(
        render_template(
            "adduser_final.html",
            name=name,
            telegram_id=telegram_id,
            role=role,
        )
    )

    # Cleanup session
    await state.clear()


@dp.message()
@skip_downtime
@require_user
async def unknown_message_handler(message: Message):
    """This handler receives unknown commands"""
    assert message.from_user is not None
    logger.debug("Handling unknown command. %s", log_userinfo(message))
    await message.answer(render_template("unknown.html", cmd_help=COMMAND_HELP))


async def notify_users_downtime(bot: Bot, downtime: int) -> None:
    """Function to notify users about downtime.

    Args:
        bot (Bot): Bot instance.
        downtime (int): Downtime in seconds.
    """
    # Get human readable downtime
    downtime_str = format_seconds(downtime)

    # Get users to notify
    users = await db.get_all_users()
    if not isinstance(users, Iterable):
        logger.error("CFailed to get users to notify about downtime")
        return

    # Iterate through users
    logger.info("Starting sending downtime notifications")
    for user in users:
        telegram_id = user["telegram_id"]
        try:
            logger.debug(
                "Sending downtime notification to user with telegram_id: %d",
                telegram_id,
            )
            await bot.send_message(
                telegram_id, render_template("downtime.html", downtime=downtime_str)
            )
        except TelegramForbiddenError:
            logger.debug(
                "Can not send downtime notification to user with telegram_id: %d",
                telegram_id,
            )
        await asyncio.sleep(DOWNTIME_NOTIFICATION_TIMEOUT)


async def start_bot(downtime: int):
    """Function to start bot."""
    logger.info("Application start")

    # Connect to database
    logger.info("Starting database")
    await db.connect()

    # Initialize Bot instance
    logger.info("Initializing bot")
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    try:
        # Set bot commands
        await bot.set_my_commands(
            [
                BotCommand(command=CommandStart().commands[0], description="Start bot"),
                BotCommand(command=COMMAND_ID, description="Get telegram ID"),
                BotCommand(command=COMMAND_HELP, description="Get bot help"),
            ]
        )

        # Skip messages during downtime
        await bot.get_updates(offset=None, limit=1, timeout=0)

        # Notify users about downtime if needed (downtime < 0 if corrupted downtime)
        if downtime > MIN_DOWNTIME or downtime < 0:
            logger.info("Notifying user about downtime")
            asyncio.create_task(notify_users_downtime(bot, downtime))

        # Start bot
        logger.info("Starting bot")
        await dp.start_polling(bot)
    finally:
        # Close bot
        logger.info("Closing bot session")
        await bot.session.close()

        # Close database
        logger.info("Stopping database")
        await db.close()


def main():
    """Main application function."""
    # Check until network available
    logger.info("Waiting for network")
    wait_for_network()
    logger.info("Network available")

    # Get downtime
    downtime = get_downtime()
    logger.info("Server was down for %d seconds", downtime)

    # Start timer
    start_timer()

    # Start network tracker
    start_network_tracker(getpid())

    # Start bot
    asyncio.run(start_bot(downtime))


if __name__ == "__main__":
    main()
