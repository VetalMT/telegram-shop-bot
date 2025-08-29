import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://USER:PASSWORD@HOST:PORT/DBNAME"
)
