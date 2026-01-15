"""Main application script"""

import asyncio
from functools import wraps

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import BotCommand, Message

from env_vars import BOT_TOKEN, OWNER_USER_ID
from log import logger

# Bot dispatcher
dp = Dispatcher()


def only_for_whitelisted(handler):
    """Decorator to only allow whitelisted users to send requests"""

    # TODO: Implement user whitelist

    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user is None:
            logger.error("Can not get user info from message")
            return
        if message.from_user.id != OWNER_USER_ID:
            logger.debug("Access denied for user: %d", message.from_user.id)
            return
        return await handler(message, *args, **kwargs)

    return wrapper


def only_for_owner(handler):
    """Decorator to only allow owner to send requests"""

    @wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user is None:
            logger.error("Can not get user info from message")
            return
        if message.from_user.id != OWNER_USER_ID:
            logger.debug("Access denied for user: %d", message.from_user.id)
            return
        return await handler(message, *args, **kwargs)

    return wrapper


@dp.message(CommandStart())
@only_for_whitelisted
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command"""
    if message.from_user is None:
        logger.error("Can not get user info from message")
        return
    logger.debug("Starting new chat. Requested by: %s", message.from_user.username)
    await message.answer("Hello World!")


async def main():
    """Main application function"""
    logger.info("Application start")

    # Initialize Bot instance
    logger.info("Initializing bot")
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # Set bot commands
    await bot.set_my_commands(
        [
            BotCommand(command=CommandStart().commands[0], description="Start bot"),
        ]
    )

    # Start bot
    logger.info("Starting bot")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
