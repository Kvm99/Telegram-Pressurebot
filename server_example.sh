#!/bin/bash

export TOKEN="your_telegram_bot_token"

export PROXY_URL='your_proxy_url'
export PROXY_USERNAME='your_proxy_url'
export PROXY_PASSWORT='your_proxy_password'

export POSTGRES_USER='your_postgres_user'
export POSTGRES_PASSW='your_postgres_passw'
export DB_NAME='your_postgres_db_name'

python3 telegram_pressure_bot.py
