from typing import Optional

import aiohttp
import logging

from app.utils.jwt_utils import decode_token

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ProfileApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def fetch_user_profile(self, token: str) -> Optional[dict]:
        decoded_token = decode_token(token)
        if not decoded_token:
            logging.error("Ошибка декодирования токена")
            return None

        url = f"{self.base_url}/profile/{decoded_token['user_id']}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /profile/{{user_id}} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return None

    async def get_user_token(self, user_id: int) -> Optional[str]:
        url = f"{self.base_url}/token/{user_id}"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                logging.info(f"[API] GET /token/{user_id} → {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return data.get("access_token")
                else:
                    logging.warning(f"[API] Token not received for user_id={user_id}")
                    return None

    async def update_user_profile(self, user_id: int, new_username: str, token: str) -> Optional[dict]:
        url = f"{self.base_url}/profile/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"username": new_username}

        async with aiohttp.ClientSession() as session:
            async with session.put(url, json=payload, headers=headers) as response:
                logging.info(f"[API] PUT /profile/{user_id} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Error: {await response.text()}")

    async def logout_user(self, user_id: int, token: str) -> Optional[dict]:
        url = f"{self.base_url}/logout/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                logging.info(f"[API] POST /logout/{user_id} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Logout error: {await response.text()}")
                    return None

    async def reset_token_api(self, user_id: int, token: str) -> Optional[dict]:
        url = f"{self.base_url}/reset-token/{user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers) as response:
                logging.info(f"[API] POST /reset-token/{user_id} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Reset token error: {await response.text()}")
                    return None


