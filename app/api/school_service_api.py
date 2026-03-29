import aiohttp
import logging
from typing import Optional
from app.database.schemas import SchoolServiceOut, SchoolServiceCreateRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class SchoolServiceApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/school_services"

    async def get_all(self, user_id: int, token: str) -> Optional[list[dict]] | dict:
        url = f"{self.base_url}/list?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /school_services/list → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logging.error(f"[API] Error: {await response.text()}")
                return None

    async def get_by_id(self, user_id: int, service_id: int, token: str) -> Optional[dict] | dict:
        url = f"{self.base_url}/{service_id}?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /school_services/{service_id} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logging.error(f"[API] Error: {await response.text()}")
                return None

    async def add(self, request: SchoolServiceCreateRequest) -> Optional[SchoolServiceOut] | dict:
        url = f"{self.base_url}/add"
        headers = {
            "Authorization": f"Bearer {request.token}",
            "Content-Type": "application/json"
        }

        data = request.model_dump()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                logging.info(f"[API] POST /school_services/add → {response.status}")
                if response.status == 201:
                    json_data = await response.json()
                    return SchoolServiceOut(**json_data)
                elif response.status == 401:
                    return {"error": "token_expired"}
                logging.error(f"[API] Error: {await response.text()}")
                return None


# async def get_school_service_by_id_api(user_id: int, service_id: int, token: str) -> dict | None:
#     """Получить услугу/товар по ID"""
#     url = f"{BASE_URL}/{service_id}?user_id={user_id}"
#     headers = {"Authorization": f"Bearer {token}"}
#
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, headers=headers) as response:
#             logging.info(f"Get school service {service_id} response status: {response.status}")
#             if response.status == 200:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"Get school service {service_id} error response: {await response.text()}")
#                 return None
#
# async def add_school_service_api(service_data: SchoolServiceCreateRequest) -> SchoolServiceOut | dict | None:
#     """Добавить новую услугу"""
#     url = f"{BASE_URL}/add"
#     token = str(service_data.token)
#
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
#
#     data = {
#         "user_id": service_data.user_id,
#         "title": service_data.title,
#         "description": service_data.description,
#         "price": service_data.price,
#         "token": service_data.token
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, json=data, headers=headers) as response:
#             logging.info(f"Add service response status: {response.status}")
#
#             if response.status == 201:
#                 json_data = await response.json()
#                 return SchoolServiceOut(**json_data)
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"Add school service error response: {await response.text()}")
#                 return None

