"""Constants module"""

from os import getenv

# Check if debug is true
DEBUG: bool = getenv("DEBUG", "").strip().lower() == "true"

# Common error response
COMMON_ERROR_RESPONSE: tuple = ("", 404)

# Common success response
COMMON_SUCCESS_RESPONSE: tuple = ("", 200)

# Logger name
LOGGER_NAME: str = "RECEIVER"
