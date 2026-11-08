#!/usr/bin/env bash

isort . --profile black --skip .venv
black . --extend-exclude '/\.venv/'
