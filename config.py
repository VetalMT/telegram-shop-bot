import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

# URL бази даних PostgreSQL (наприклад, у Render або Heroku)
DATABASE_URL = os.getenv("DATABASE_URL")
