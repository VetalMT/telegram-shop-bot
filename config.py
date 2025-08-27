import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shop_db_j2lo_user:password@dpg-d2n2u92li9vc73chmkqg-a:5432/shop_db_j2lo")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "https://telegram-shop-bot-z03b.onrender.com")
PORT = int(os.getenv("PORT", 8000))