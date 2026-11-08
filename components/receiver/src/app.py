"""Main application module"""

import logging
from sys import stdout

from flask import Flask
from werkzeug.exceptions import HTTPException

from constants import COMMON_ERROR_RESPONSE, COMMON_SUCCESS_RESPONSE, DEBUG, LOGGER_NAME

# Create logger
logger = logging.getLogger(LOGGER_NAME)
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
logger.handlers.clear()
handler = logging.StreamHandler(stdout)
handler.setFormatter(
    logging.Formatter("[%(asctime)s - %(name)s - %(levelname)s]: %(message)s")
)
logger.addHandler(handler)

# Create Flask app
app = Flask(__name__)


@app.errorhandler(Exception)
def errorhandler(err):
    """Error handler"""
    if not isinstance(err, HTTPException):
        logger.error("Error occured: %s", err)
    return COMMON_ERROR_RESPONSE


@app.route("/health")
def health():
    """Healthcheck route"""
    return COMMON_SUCCESS_RESPONSE
