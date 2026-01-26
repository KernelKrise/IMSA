# IMSA

IMSA (Is My Server Alive?) is a Telegram bot that helps you check the availability and runtime information of your server. You run the bot on your server, and if it replies, the server is up. If it stops replying, the server may be down or unreachable, it will notify you when it is back online.

## Prerequisites

Before using IMSA you need:

- A running server
- Docker and Docker Compose
- A Telegram Bot Token from [BotFather](https://t.me/BotFather)
- Your Telegram user ID

## Installation

Clone the Repository

```shell
git clone https://github.com/KernelKrise/IMSA.git
cd IMSA
```

Copy the example environment file:

```shell
cp env_example .env
```

Open `.env` and set the following:

- `BOT_TOKEN` — your Telegram bot token from BotFather
- `OWNER_USER_ID` — your Telegram user ID (can be fetched with user ID bots)

Example .env format:

```shell
BOT_TOKEN=123456789:ABCDEF...
OWNER_USER_ID=987654321
```

Launch with Docker Compose:

```shell
docker compose up -d
```

## Update

To update your IMSA installation, use the following command:

```shell
git pull
docker compose up -d --build --force-recreate
```

## User Guide

Commands available:

- `/start` – Greeting message
- `/help` – Help message
- `/id` - Get your Telegram ID
- `/check` - Check server runtime information (registration required)

Also, if you are registered user, you will recieve notification when server back online

> To register, send your telegram ID to administrator

## Admin guide

Admin has access to all user commands along with:

- `/add_user` - Register user
- `/get_users` - Get all registered users
- `/delete_user` - Delete user
- `/cancel` - Cancel command

## TODO
