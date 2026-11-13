# Base image
FROM python:3.14-slim AS base

# Define environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.5.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    APP_WORKDIR=/app \
    UID=1000 \
    USERNAME=app

# Create unprivileged group
RUN groupadd --gid ${UID} ${USERNAME}

# Create unprivileged user
RUN useradd --no-create-home --uid ${UID} --gid ${UID} ${USERNAME}

# Install poetry
RUN pip3 install poetry==${POETRY_VERSION}

# Install dependencies
RUN DEBIAN_FRONTEND=noninteractive apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*


FROM base AS builder

# Create poetry directory
WORKDIR ${POETRY_HOME}

# Copy project sources
COPY pyproject.toml poetry.lock ./

# Build poetry venv
RUN poetry install --no-root


FROM base AS release

# Copy poetry environment
COPY --from=builder ${POETRY_HOME}/.venv ${POETRY_HOME}/.venv

# Setup workdir
WORKDIR ${APP_WORKDIR}

# Copy sources
COPY ./src/ ./

# Setup workdir permissions
RUN chown ${UID}:${UID} -R ${APP_WORKDIR}

# Set user
USER ${USERNAME}

# Set entrypoint
ENTRYPOINT ["bash"]

# Set cmd
CMD [ "entrypoint.sh" ]
