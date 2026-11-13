#!/usr/bin/env bash

# Exit on errors
set -euo pipefail

# Logging
ilog() {
    echo -e "[*] ${1}"
}

# Variables
HOST=0.0.0.0
PORT=8000
WORKERS=$(nproc)
THREADS=2

# Activate poetry venv
ilog "Activating poetry venv"
source "${POETRY_HOME}/.venv/bin/activate"

# Start main application
ilog "Starting main application"
exec gunicorn \
    --no-control-socket \
    --bind "${HOST}:${PORT}" \
    --workers "${WORKERS}" \
    --threads "${THREADS}" \
    app:app
