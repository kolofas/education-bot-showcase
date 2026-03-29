import aiohttp
import logging
from typing import Optional

from app.database.schemas import UserLoginRequest, UserLoginResponse

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class AuthenticationApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    async def authenticate(self, request: UserLoginRequest) -> Optional[UserLoginResponse | dict]:
        url = f"{self.base_url}/authenticate/"
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=request.model_dump()) as response:
                logging.info(f"[API] POST /authenticate → {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return UserLoginResponse(**data)
                elif response.status == 401:
                    return {"error": "invalid_credentials"}
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return None

    async def is_authorized(self, user_id: int) -> bool:
        url = f"{self.base_url}/check-auth/{user_id}"

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    logging.info(f"[API] GET /check-auth/{user_id} → {response.status}")
                    if response.status == 200:
                        json_data = await response.json()
                        return json_data.get("authorized", False)
                    return False
        except Exception as e:
            logging.error(f"Ошибка запроса к API авторизации: {e}")
            return False

    async def get_token(self, user_id: int) -> str | None:
        url = f"{self.base_url}/token/{user_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("access_token")
                else:
                    return None
