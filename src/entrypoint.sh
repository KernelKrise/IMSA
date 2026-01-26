#!/bin/bash

# Logging
ilog(){
    echo "[*] $1"
}

# Activate poetry venv
ilog "Activating poetry environment"
source "${POETRY_HOME}/.venv/bin/activate"

# Start application
ilog "Starting application"
python3 main.py

ilog "Bye!"
