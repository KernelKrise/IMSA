"""Module with helper functions"""

import asyncio
import re

from jinja2 import Environment, FileSystemLoader

from log import logger

# Jinja2 environment
jinja2_env = Environment(
    loader=FileSystemLoader("templates"),
    autoescape=True,
)


def render_template(template: str, **context) -> str:
    """Render jinja2 template.

    Args:
        template (str): Template filename.

    Returns:
        str: Rendered template.
    """
    return jinja2_env.get_template(template).render(**context)


async def get_uptime() -> str | None:
    """Get server uptime.

    Returns:
        str: Server uptime or None on error.
    """
    # Execute uptime command
    process = await asyncio.create_subprocess_exec(
        "uptime", "-p", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    # Read stdout and stderr
    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        return stdout.decode(errors="ignore").strip().removeprefix("up ")
    else:
        logger.error("Uptime error: %s", stderr.decode(errors="ignore").strip())
        return None


def is_valid_string(to_validate: str, max_length=128) -> bool:
    """Validates string. Only lowercase, uppercase, numbers and underscore allowed.

    Args:
        to_validate (str): String to validate
        max_length (int, optional): Max allowed string length. Defaults to 128.

    Returns:
        bool: True if valid, False if invalid.
    """
    # Validate length
    if len(to_validate) > max_length:
        return False

    # Validate symbols
    return bool(re.fullmatch(r"[a-zA-Z0-9_]+", to_validate))


def format_seconds(seconds: int) -> str:
    """Format seconds to human readable format.

    Args:
        seconds (int): Seconds to covert.

    Returns:
        str: Human readable time format.
    """

    # Calculate metrics
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    # Compose result
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes or not parts:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")

    return ", ".join(parts)
