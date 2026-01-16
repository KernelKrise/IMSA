"""Module with helper functions"""

from jinja2 import Environment, FileSystemLoader

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
