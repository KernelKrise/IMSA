# Base stage
FROM python:3.14-slim-trixie AS base

# Environment variables
ENV POETRY_VERSION=2.2.1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_HOME=/opt/poetry \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    USERNAME=user \
    UID=1000

# Create a new user and group
RUN groupadd -r "${USERNAME}" && useradd -u "${UID}" -r -g "${USERNAME}" "${USERNAME}"

# Install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt update -y && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends \
    procps \
    && rm -rf /var/lib/apt/lists/*


# Builder stage
FROM base AS builder

# Install poetry
RUN pip3 install "poetry==${POETRY_VERSION}"

# Set workdir for poetry
WORKDIR "${POETRY_HOME}"

# Copy poetry files
COPY pyproject.toml poetry.lock ./

# Install poetry packages
RUN poetry install --no-root


# Production stage
FROM base AS production

# Copy venv from builder stage
COPY --from=builder "${POETRY_HOME}/.venv" "${POETRY_HOME}/.venv"

# Set workidr
WORKDIR /app

# Copy source code
COPY ./src .

# Set permissions
RUN chmod -R "750" . && chown -R "${USERNAME}":"${USERNAME}" .

# Set user
USER "${USERNAME}"

# Start entrypoint script
CMD ["bash", "entrypoint.sh"]
