"""Database management module"""

from datetime import datetime, timezone
from logging import getLogger

from psycopg import Error
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from constants import LOGGER_NAME, POSTGRES_URL
from models import PingData

# Create database connection pool
pool = ConnectionPool(
    POSTGRES_URL, min_size=1, max_size=16, kwargs={"row_factory": dict_row}, open=True
)

# Get logger
logger = getLogger(LOGGER_NAME)


def update_agent_last_seen(ping_data: PingData) -> bool:
    """Update agent's 'last_seen' timestamp in database.

    Args:
        ping_data (PingData): Ping data object.

    Returns:
        bool: True if success, False on error.
    """
    try:
        with pool.connection() as conn:
            cur = conn.execute(
                "UPDATE agents SET last_seen = %s WHERE key = %s",
                (datetime.now(timezone.utc), ping_data.key),
            )
            return cur.rowcount > 0
    except Error as e:
        logger.error("Failed to update agent data:\n%s", e)
        return None
