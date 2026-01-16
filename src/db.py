"""This module is for database handling"""

from functools import wraps
from typing import Iterable

import aiosqlite

from constants import OWNER_DEFAULT_USERNAME, ROLE_ADMIN, ROLE_USER, SQLITE_DB_FILEPATH
from env_vars import OWNER_USER_ID
from log import logger


def db_safe(func):
    """Decorator to wrap async DB methods in try/except."""

    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        # Execute target function
        try:
            return await func(self, *args, **kwargs)
        except aiosqlite.Error as e:
            logger.error("Database error in %s: %s", func.__name__, str(e))
            return False

    return wrapper


class IMSADB:
    """Database handling class"""

    def __init__(self, db_filepath: str = SQLITE_DB_FILEPATH):
        self.db_filepath: str = db_filepath
        self._db: aiosqlite.Connection | None = None

    def db(self) -> aiosqlite.Connection:
        """Database connection function.

        Raises:
            RuntimeError: Error if database connection not initialized.

        Returns:
            aiosqlite.Connection: aiosqlite connection.
        """
        if self._db is None:
            raise RuntimeError("Database not connected")
        return self._db

    @db_safe
    async def connect(self) -> bool:
        """Open the database connection and initialize tables.

        Returns:
            bool: True on success, False on error.
        """
        # Connect to database
        logger.info("Connecting to database")
        self._db = await aiosqlite.connect(self.db_filepath)

        # Set row factory
        self._db.row_factory = aiosqlite.Row

        return await self.init_db()

    @db_safe
    async def close(self) -> bool:
        """Close the database connection.

        Returns:
            bool: True on success, False on error.
        """
        # Close connection
        logger.info("Closing database connection")
        await self.db().close()
        return True

    @db_safe
    async def init_db(self) -> bool:
        """Create needed tables if they do not exist.

        Returns:
            bool: True on success, False on error.
        """
        # Initialize database
        logger.info("Initializing database")
        await self.db().execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            )
            """
        )
        await self.db().commit()

        # Ensuring admin exists
        await self.ensure_admin()
        return True

    @db_safe
    async def ensure_admin(self) -> bool:
        """Ensures that admin exists.

        Returns:
            bool: True on success, False on error.
        """
        logger.info("Ensuring admin exists")
        # Get admin user
        async with self.db().execute(
            "SELECT 1 FROM users WHERE role = ? LIMIT 1", (ROLE_ADMIN,)
        ) as cursor:
            admin_exists = await cursor.fetchone()

        # Check if admin exists
        if admin_exists:
            return True

        # Create admin
        logger.info("Creating admin")
        return await self.add_user(OWNER_USER_ID, OWNER_DEFAULT_USERNAME, ROLE_ADMIN)

    @db_safe
    async def get_all_users(self) -> Iterable[aiosqlite.Row] | bool:
        """Fetch all users.

        Returns:
            Iterable[aiosqlite.Row] | bool: List of user rows or False on error.
        """
        # Fetch all users
        logger.debug("Fetching all users")
        async with self.db().execute("SELECT * FROM users") as cursor:
            return await cursor.fetchall()

    @db_safe
    async def add_user(self, telegram_id: int, name: str, role: str) -> bool:
        """Add user to database.

        Args:
            telegram_id (int): Telegram ID.
            name (str): Name.
            role (str): User role.

        Returns:
            bool: True on success, False on error.
        """
        # Add user to database
        logger.info("Adding user with telegram_id: %s and role: %s", telegram_id, role)
        await self.db().execute(
            "INSERT INTO users (telegram_id, name, role) VALUES (?, ?, ?)",
            (telegram_id, name, role),
        )
        await self.db().commit()
        return True

    @db_safe
    async def get_user(self, telegram_id: int) -> aiosqlite.Row | bool:
        """Fetch a user by Telegram ID.

        Args:
            telegram_id (int): Telegram ID.

        Returns:
            aiosqlite.Row | bool: User data or False on error.
        """
        # Get user by Telegram ID
        logger.debug("Fetching user with telegram_id: %s", telegram_id)
        async with self.db().execute(
            "SELECT * FROM users WHERE telegram_id = ?", (telegram_id,)
        ) as cursor:
            return await cursor.fetchone() or False

    @db_safe
    async def delete_user(self, telegram_id: int) -> bool:
        """Delete a user by Telegram ID.

        Args:
            telegram_id (int): Telegram ID.

        Returns:
            bool: True on success, False on error.
        """
        # Delete user by Telegram ID
        logger.info("Deleting user with telegram_id: %s", telegram_id)
        cursor = await self.db().execute(
            "DELETE FROM users WHERE telegram_id = ?", (telegram_id,)
        )
        await self.db().commit()
        return cursor.rowcount > 0

    async def get_role(self, telegram_id: int) -> str | None:
        """Get sender role.

        Args:
            telegram_id (int): Telegram ID.

        Returns:
            str | None: Role string or None on error.
        """

        # Get user info
        user_info = await self.get_user(telegram_id)
        if isinstance(user_info, bool):
            return None
        return user_info["role"]

    async def is_user(self, telegram_id: int) -> bool:
        """Check if sender is user.

        Args:
            telegram_id (int): Telegram ID.

        Returns:
            bool: True if user or admin, False if not.
        """
        # Get sender role
        sender_role = self.get_role(telegram_id)

        if sender_role in (ROLE_ADMIN, ROLE_USER):
            return True
        return False

    async def is_admin(self, telegram_id: int) -> bool:
        """Check if sender is admin.

        Args:
            telegram_id (int): Telegram ID.

        Returns:
            bool: True if admin, False if not.
        """
        # Get sender role
        sender_role = self.get_role(telegram_id)

        if sender_role == ROLE_ADMIN:
            return True
        return False
