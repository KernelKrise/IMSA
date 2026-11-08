"""Database management module"""

from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from constants import POSTGRES_URL

# Create database connection pool
pool = ConnectionPool(
    POSTGRES_URL, min_size=1, max_size=16, kwargs={"row_factory": dict_row}, open=True
)
