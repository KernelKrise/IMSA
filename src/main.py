"""Main application script"""

import asyncio
from functools import wraps

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import BotCommand, Message

from constants import COMMAND_HELP, COMMAND_ID
from db import IMSADB
from env_vars import BOT_TOKEN
from helpers import render_template
from log import log_userinfo, logger

# Bot dispatcher
dp = Dispatcher()

# Database
db = IMSADB()


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
        if db.is_user(message.from_user.id) is False:
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
        if db.is_admin(message.from_user.id) is False:
            logger.debug("Admin access denied. %s", log_userinfo(message))
            return
        return await handler(message, *args, **kwargs)

    return wrapper


@dp.message(Command(COMMAND_ID))
async def command_id_handler(message: Message) -> None:
    """This handler receives messages with 'id' command"""
    assert message.from_user is not None

    logger.debug("Sending user ID. %s", log_userinfo(message))
    await message.answer(render_template("id.html", user_id=message.from_user.id))


@dp.message(CommandStart())
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
async def command_help_handler(message: Message) -> None:
    """This handler receives messages with 'help' command"""
    assert message.from_user is not None
    logger.debug("Sending help message. %s", log_userinfo(message))

    if db.is_admin(message.from_user.id):
        await message.answer(
            render_template(
                "help_admin.html",
                cmd_start=CommandStart().commands[0],
                cmd_help=COMMAND_HELP,
                cmd_id=COMMAND_ID,
            )
        )
    elif db.is_user(message.from_user.id):
        await message.answer(
            render_template(
                "help_user.html",
                cmd_start=CommandStart().commands[0],
                cmd_help=COMMAND_HELP,
                cmd_id=COMMAND_ID,
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


async def main():
    """Main application function"""
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


if __name__ == "__main__":
    asyncio.run(main())
