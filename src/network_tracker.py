"""Network tracker module"""

from multiprocessing import Process
from os import kill
from signal import SIGKILL
from time import sleep

from constants import NETWORK_TRACKER_TIMEOUT
from helpers import network_available
from log import logger


def network_tracker(main_pid: int) -> None:
    """Network timer. Terminates main process on network issue"""

    # Start loop
    while True:
        # Check if network available
        if not network_available():
            logger.info(
                "Network unavaliable, terminating main application: %d", main_pid
            )
            kill(main_pid, SIGKILL)
        # Sleep
        sleep(NETWORK_TRACKER_TIMEOUT)


def start_network_tracker(main_pid: int) -> None:
    """Start network tracker as daemon. If network down, it will terminate main application."""
    # Create tracker process
    p = Process(target=network_tracker, daemon=True, args=(main_pid,))
    logger.info("Starting network tracker process")
    p.start()
