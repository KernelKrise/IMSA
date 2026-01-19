"""This module it for timer tracking (downtime)"""

from multiprocessing import Process
from os import fsync, path
from time import sleep, time

from constants import TIMER_FILEPATH, TIMER_TIMEOUT
from log import logger


def timer() -> None:
    """Timer. Writes current timestamp periodically"""

    # Start loop
    while True:
        # Get current timestamp
        current_time = round(time())

        # Write current timestamp to file
        with open(TIMER_FILEPATH, "w", encoding="utf-8") as f:
            f.write(str(current_time))
            f.flush()
            fsync(f.fileno())

        # Sleep
        sleep(TIMER_TIMEOUT)


def start_timer() -> None:
    """Start timer process as daemon"""
    # Create timer process
    p = Process(target=timer, daemon=True)
    logger.info("Starting timer process")
    p.start()


def get_downtime() -> int:
    """Get downtime based on saved timestump.

    Returns:
        int: Downtime in seconds. 0 on error.
    """
    # Check if saved timestamp exists
    if not path.exists(TIMER_FILEPATH):
        logger.info("Saved timestamp not found")
        return 0

    # Get current timestamp
    current_time = round(time())

    # Read saved timestamp
    with open(TIMER_FILEPATH, "r", encoding="utf-8") as f:
        saved_time = f.read()

    # Convert timestamp to int
    try:
        saved_time = int(saved_time)
    except ValueError:
        logger.error("Failed to read saved timestamp")
        return 0

    # Calculate downtime
    return current_time - saved_time
