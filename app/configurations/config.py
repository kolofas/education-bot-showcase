from dotenv import load_dotenv
import os

load_dotenv() # Загружаем переменные из .env

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://showcase_app:showcase_app@localhost:5432/showcase_app",
)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-dev")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 60))

BOT_TOKEN = os.getenv("BOT_TOKEN")
