"""Module with helper functions"""

import asyncio

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
        return stdout.decode(errors="ignore").strip()
    else:
        logger.error("Uptime error: %s", stderr.decode(errors="ignore").strip())
        return None
