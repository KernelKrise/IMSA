"""Utils module"""

from json import dumps
from logging import getLogger

from flask import Response

from constants import LOGGER_NAME

logger = getLogger(LOGGER_NAME)


def compose_response(body: dict, status: int = 200) -> Response:
    """Compose JSON response.

    Args:
        body (dict): Response JSON.
        status (int, optional): HTTP status. Defaults to 200.

    Returns:
        Response: Flask Response object.
    """

    # Make response
    return Response(
        response=dumps(body),
        status=status,
        mimetype="application/json",
    )
