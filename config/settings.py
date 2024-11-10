import os
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

API_URL = "https://incentive-backend.oceanprotocol.com/nodes?page=1&size=1000&search="
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Проверка загрузки токена
if BOT_TOKEN is None:
    raise ValueError("BOT_TOKEN не установлен! Убедитесь, что токен задан в переменных окружения.")
