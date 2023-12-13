from dotenv import load_dotenv
import os

load_dotenv()

HOST = os.getenv("DB_HOST")
USER = os.getenv("DB_USERNAME")
PASSWORD = os.getenv("DB_PASSWORD")
DATABASE = os.getenv("DB_NAME")
TOKEN = os.environ.get("TOKEN")
ssl = os.environ.get("IS_TSL")
IS_TSL = True if ssl == "1" else False if ssl == "0" else None
