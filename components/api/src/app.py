"""Main application module"""

import logging
from sys import stdout

from flask import Flask, request
from pydantic import ValidationError

from constants import (
    DEBUG,
    LOGGER_NAME,
)
from db import delete_agent, register_agent
from models import Agent, AgentDeletionRequest
from utils import compose_response

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
    return compose_response({"status": "healthy"})


@app.route("/agent/register", methods=["POST"])
def agent_register():
    """Agent registration route"""

    # Validate request data
    try:
        request_data: Agent = Agent.model_validate_json(request.get_data())
    except ValidationError as ex:
        logger.debug("Agent registration request data validation error:\n%s", ex)
        return compose_response(
            {"error": "Agent registration request data validation error"}, status=400
        )
    logger.debug("Agent registration request data: %s", request_data.model_dump_json())

    # Register agent
    agent_data = register_agent(request_data)
    if agent_data is None:
        return compose_response({"error": "Agent registration failed"}, status=400)

    return compose_response(agent_data.model_dump(mode="json"))


@app.route("/agent/delete", methods=["POST"])
def agent_delete():
    """Agent deletion data"""

    # Validate request data
    try:
        request_data: AgentDeletionRequest = AgentDeletionRequest.model_validate_json(
            request.get_data()
        )
    except ValidationError as ex:
        logger.debug("Agent deletion request data validation error:\n%s", ex)
        return compose_response(
            {"error": "Agent deletion request data validation error"}, status=400
        )
    logger.debug("Agent deletion request data: %s", request_data.model_dump_json())

    # Delete agent
    if delete_agent(request_data) is False:
        return compose_response({"error": "Agent deletion failed"}, status=400)

    return compose_response({"status": "success"})
