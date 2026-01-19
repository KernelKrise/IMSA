# IMSA

Is My Server Alive? Telegram Bot

## Description

Deploy this bot on your server. When lauched, if the bot responds, the server is alive and you can get runtime information.
If not, the server is down. So, you can track your server availability even if it under NAT.

## Environment

You need to fill out file: `.env` as in `env_example` with the following values:

1. `BOT_TOKEN` can be obtained with: [BotFather](https://t.me/BotFather)
2. `OWNER_USER_ID` can be obtained with specialized bots

## Requirements

- Docker
- Docker Compose

## Start

```bash
docker compose up -d
```

## TODO

- Toggle downtime notification
- Track network issues
- Write documentation
