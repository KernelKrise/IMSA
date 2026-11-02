#!/usr/bin/env bash

# Logging
ilog() {
    echo -e "[*] ${1}"
}

# Activate poetry venv
ilog "Activating poetry venv"
source "${POETRY_HOME}/.venv/bin/activate"

# Start main application
python3 app.py
