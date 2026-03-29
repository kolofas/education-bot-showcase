import aiohttp
import logging
from typing import Optional

from app.database.schemas import UserRegistrationRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class RegistrationApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    async def check_user_exists(self, user_id: int) -> bool:
        """Проверяет, зарегистрирован ли пользователь"""
        url = f"{self.base_url}/check_user/{user_id}"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logging.info(f"[API] GET /check_user/{user_id} → {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return data.get("exists", False)  # Возвращаем True или False
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return False

    async def register_user(self, request: UserRegistrationRequest) -> Optional[dict]:
        """Регистрация пользователя"""
        url = f"{self.base_url}/register/"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request.model_dump()) as response:
                logging.info(f"[API] POST /register/ → {response.status}")
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return None
