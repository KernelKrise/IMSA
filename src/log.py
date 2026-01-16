"""Module to setup logging"""

import logging
from logging.handlers import RotatingFileHandler

from aiogram.types import Message

from constants import LOGFILE_BACKUP_COUNT, LOGFILE_MAX_SIZE, LOGFILE_PATH, LOGGER_NAME

# Get logger
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
)
console_handler.setFormatter(console_formatter)

# File handler
file_handler = RotatingFileHandler(
    LOGFILE_PATH, maxBytes=LOGFILE_MAX_SIZE, backupCount=LOGFILE_BACKUP_COUNT
)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter(
    "[%(asctime)s] %(levelname)s: %(message)s", datefmt="%Y-%m-%dT%H:%M:%S%z"
)
file_handler.setFormatter(file_formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)


def log_userinfo(message: Message) -> str:
    """Compose telegram user info log entry.

    Args:
        message (Message): message object.

    Returns:
        str: User info log entry.
    """
    assert message.from_user is not None
    return f"Telegram User Info: {message.from_user.id=}, {message.from_user.username=}"
