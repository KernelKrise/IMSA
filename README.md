# IMSA
Is My Server Alive? Telegram Bot

## Description

TODO: Bot is not ready yet.

## Environment

You need to fill out file: `.env` as in `env_example` with the following values:

1. `BOT_TOKEN` can be obtained with: [BotFather](https://t.me/BotFather)
2. `OWNER_USER_ID` can be obtained with specialized bots

## Requirements

You can start application in docker (recommended) or with python.

### Docker (recommended)

- Docker
- Docker Compose

### Python

- Python (>=3.11)
- Poetry

## Start

### Docker (recommended)

```bash
docker compose up -d
```

### Python

```bash
export POETRY_VIRTUALENVS_IN_PROJECT=true
poetry install --no-root
cd src
poetry run python3 main.py
```
