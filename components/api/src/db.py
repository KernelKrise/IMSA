"""Database management module"""

from logging import getLogger

from psycopg import Error
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool
from pydantic import ValidationError

from constants import LOGGER_NAME, POSTGRES_URL
from models import Agent, AgentDeletionRequest

# Create database connection pool
pool = ConnectionPool(
    POSTGRES_URL, min_size=1, max_size=16, kwargs={"row_factory": dict_row}, open=True
)

# Get logger
logger = getLogger(LOGGER_NAME)


def delete_agent(request_data: AgentDeletionRequest) -> bool:
    """Delete agent by ID.

    Args:
        request_data (AgentDeletionRequest): Agent deletion request data.

    Returns:
        bool: True on success, False on error.
    """

    logger.debug("Deleting agent id_=%d", request_data.id_)

    try:
        with pool.connection() as conn:
            cur = conn.execute(
                "DELETE FROM agents WHERE id_ = %s",
                (request_data.id_,),
            )
            return cur.rowcount > 0
    except Error as e:
        logger.error("Failed to delete agent id_=%d:\n%s", request_data.id_, e)
        return False


def register_agent(agent: Agent) -> Agent | None:
    """Register agent in database.

    Args:
        agent (Agent): Agent model object.

    Returns:
        bool: Populated Agent object on success, None on error.
    """

    logger.debug("Registering agent: %s", agent.model_dump_json())

    try:
        with pool.connection() as conn:
            cur = conn.execute(
                (
                    "INSERT INTO agents (name, key, description, status, last_seen, created_at) "
                    "VALUES (%s, %s, %s, %s, %s, %s) RETURNING *"
                ),
                (
                    agent.name,
                    agent.key,
                    agent.description,
                    agent.status,
                    agent.last_seen,
                    agent.created_at,
                ),
            )
            return Agent.model_validate(cur.fetchone())
    except Error as e:
        logger.error("Failed to insert agent data:\n%s", e)
        return None
    except ValidationError as e:
        logger.error("Failed to validate inserted agent data:\n%s", e)
        return None
