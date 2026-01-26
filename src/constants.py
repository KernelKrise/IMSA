"""Constants module"""

from os import path

DATA_DIR: str = "data"

LOGGER_NAME: str = "imsa"
LOGFILE_NAME: str = "imsa.log"
LOGFILE_PATH: str = path.join(DATA_DIR, LOGFILE_NAME)
LOGFILE_MAX_SIZE: int = 5 * 1024 * 1024
LOGFILE_BACKUP_COUNT: int = 10

SQLITE_DB_FILENAME: str = "imsa.db"
SQLITE_DB_FILEPATH: str = path.join(DATA_DIR, SQLITE_DB_FILENAME)

ROLE_USER: str = "user"
ROLE_ADMIN: str = "admin"

OWNER_DEFAULT_USERNAME: str = "OWNER"

COMMAND_ID: str = "id"
COMMAND_HELP: str = "help"
COMMAND_CHECK: str = "check"
COMMAND_ADDUSER: str = "add_user"
COMMAND_CANCEL: str = "cancel"
COMMAND_GETUSERS: str = "get_users"
COMMAND_DELUSER: str = "delete_user"

TIMER_FILENAME: str = "timer"
TIMER_FILEPATH: str = path.join(DATA_DIR, TIMER_FILENAME)
TIMER_TIMEOUT: int = 1

MIN_DOWNTIME: int = 60
DOWNTIME_NOTIFICATION_TIMEOUT: float = 0.1

NETWORK_CHECK_TARGETS: list = [("8.8.8.8", 53), ("1.1.1.1", 53)]
NETWORK_CHECK_TIMEOUT: int = 1
NETWORK_CHECK_MAX_RETRY: int = 3
