"""Utils module"""

from json import dumps
from logging import getLogger

from flask import Response

from constants import LOGGER_NAME

logger = getLogger(LOGGER_NAME)


def format_response(message: str, status: int = 200) -> Response:
    """Format response message"""

    # Make response
    return Response(
        response=dumps({"message": message}), status=status, mimetype="application/json"
    )
