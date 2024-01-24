# HelPy

Telegram support bot based on python-telegram-bot and peewee libraries.

## Installation

Create .env file in the root of project where settings.py located and set the variables:

```properties
TOKEN=telegram_bot_token
IS_TSL=1 # 1(True) or 0(False), probably only for planetscale.com?
DB_HOST=db_host
DB_USERNAME=db_username
DB_PASSWORD=db_pass
DB_NAME=db_name
DB_PORT=db_port
```

Install python requirements:

```shell
pip install -r requirements.txt
```

Tables for database will be created if run.py is executed

```shell
python run.py
```
