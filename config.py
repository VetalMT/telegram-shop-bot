import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "ВАШ_ТОКЕН_БОТА")
PORT = int(os.getenv("PORT", 8000))
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL", "https://your-app.onrender.com")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://shop_db_j2lo_user:password@dpg-d2n2u92li9vc73chmkqg-a:5432/shop_db_j2lo")