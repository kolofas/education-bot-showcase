import aiohttp
import logging
from typing import Optional
from app.database.schemas import BonusCreateRequest

logger = logging.getLogger(__name__)

class BonusApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/bonuses"

    async def get_all(self, user_id: int, token: str) -> Optional[list[dict]] | dict:
        url = f"{self.base_url}/list?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logger.info(f"[API] GET /bonuses/list → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logger.error(f"[API] Error: {await response.text()}")
                return None

    async def get_by_id(self, user_id: int, bonus_id: int, token: str) -> Optional[dict] | dict:
        url = f"{self.base_url}/{bonus_id}?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logger.info(f"[API] GET /bonuses/{bonus_id} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logger.error(f"[API] Error: {await response.text()}")
                return None

    async def add(self, request: BonusCreateRequest) -> Optional[dict] | dict:
        url = f"{self.base_url}/add"
        headers = {
            "Authorization": f"Bearer {request.token}",
            "Content-Type": "application/json"
        }

        data = request.model_dump()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                logger.info(f"[API] POST /bonuses/add → {response.status}")
                if response.status == 201:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logger.error(f"[API] Error: {await response.text()}")
                return None

# # Получить список бонусов
# async def get_bonus_list_api(user_id: int, token: str) -> list[dict] | None:
#     url = f"{BASE_URL}/list?user_id={user_id}"
#     headers = {"Authorization": f"Bearer {token}"}
#
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, headers=headers) as response:
#             logging.info(f"[API] Get bonuses response status: {response.status}")
#             if response.status == 200:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"[API] Error response: {await response.text()}")
#                 return None
#
# # Получить бонус по ID
# async def get_bonus_by_id_api(user_id: int, bonus_id: int, token: str) -> dict | None:
#     url = f"{BASE_URL}/{bonus_id}?user_id={user_id}"
#     headers = {"Authorization": f"Bearer {token}"}
#
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, headers=headers) as response:
#             logging.info(f"[API] Get bonus {bonus_id} status: {response.status}")
#             if response.status == 200:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"[API] Error response: {await response.text()}")
#                 return None
#
# # Добавить бонус
# async def add_bonus_api(bonus_data: BonusCreateRequest) -> dict | None:
#     url = f"{BASE_URL}/add"
#     token = bonus_data.token
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
#
#     data = {
#         "user_id": bonus_data.user_id,
#         "title": bonus_data.title,
#         "description": bonus_data.description,
#         "action_text": bonus_data.action_text,
#         "token": bonus_data.token,
#         "is_active": bonus_data.is_active
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, json=data, headers=headers) as response:
#             logging.info(f"[API] Add bonus response status: {response.status}")
#             if response.status == 201:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"[API] Error response: {await response.text()}")
#                 return None
