"""Constants module"""

from os import getenv


def getenv_required(env_var_name: str) -> str:
    """Get environment variable value, if does not exist -> error

    Args:
        env_var_name (str): Environment variable name.

    Returns:
        str: Environment variable value.
    """
    # Get environment variable value
    env_var_value: str | None = getenv(env_var_name, None)

    # Validate environment variable value
    if env_var_value is None:
        raise EnvironmentError(f"Required environment variable '{env_var_name}' unset")

    return env_var_value


# Check if debug is true
DEBUG: bool = getenv("DEBUG", "").strip().lower() == "true"

# PostgreSQL URL
POSTGRES_URL: str = getenv_required("POSTGRES_URL")

# Logger name
LOGGER_NAME: str = "RECEIVER"

# Ping route
PING_ROUTE: str = "/ping"
