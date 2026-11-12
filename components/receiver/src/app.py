"""Main application module"""

import logging
from sys import stdout

from flask import Flask, request
from pydantic import ValidationError

from constants import (
    DEBUG,
    LOGGER_NAME,
    PING_ROUTE,
)
from db import update_agent_last_seen
from models import PingData
from utils import format_response

# Create logger
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
logger.handlers.clear()
handler = logging.StreamHandler(stdout)
handler.setFormatter(
    logging.Formatter("[%(asctime)s | %(name)s | %(levelname)s]: %(message)s")
)
logger.addHandler(handler)

# Create Flask app
app = Flask(__name__)


@app.route("/health")
def health():
    """Healthcheck route"""
    return format_response("healthy")


@app.route(PING_ROUTE, methods=["POST"])
def ping():
    """Ping route"""

    # Validate ping data
    try:
        ping_data: PingData = PingData.model_validate_json(request.get_data())
    except ValidationError as ex:
        logger.debug("Ping data validation error:\n%s", ex)
        return format_response("Ping data validation error", status=400)
    logger.debug("Ping data: %s", ping_data.model_dump_json())

    # Update agent's last_seen
    if update_agent_last_seen(ping_data.agent_id) is False:
        logger.debug(
            "Agent's %s 'last_seen' field failed to update", ping_data.agent_id
        )
        return format_response("Failed to process ping", status=400)

    return format_response("ok")
