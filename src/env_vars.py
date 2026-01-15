"""Module to handle environment variables"""

from os import getenv
from sys import exit as sys_exit

from log import logger


def getenv_strict(var_name: str) -> str:
    """Get environment variable, raise error if not found or empty.

    Args:
        var_name (str): Environmant variable name.

    Returns:
        str: Environmant variable value.
    """

    # Get environment variable
    value = getenv(var_name, None)

    # Check environment variable
    if value is None or value == "":
        logger.error("Environment variable %s is not set", var_name)
        sys_exit(1)

    return value


BOT_TOKEN: str = getenv_strict("BOT_TOKEN")
OWNER_USER_ID: int = int(getenv_strict("OWNER_USER_ID"), 10)
