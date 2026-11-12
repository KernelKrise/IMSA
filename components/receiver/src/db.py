"""Database management module"""

from datetime import datetime, timezone
from uuid import UUID

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from constants import POSTGRES_URL

# Create database connection pool
pool = ConnectionPool(
    POSTGRES_URL, min_size=1, max_size=16, kwargs={"row_factory": dict_row}, open=True
)


def update_agent_last_seen(agent_id: UUID) -> bool:
    """Update agent's 'last_seen' timestamp in database.

    Args:
        agent_id (UUID): Agent ID.

    Returns:
        bool: True if success, False on error.
    """

    with pool.connection() as conn:
        cur = conn.execute(
            "UPDATE agents SET last_seen = %s WHERE guid = %s",
            (datetime.now(timezone.utc), agent_id),
        )
        return cur.rowcount > 0
