from typing import Optional

import aiohttp
import logging
from app.database.schemas import MaterialData, MaterialCreateRequest

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")


class MaterialsApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/materials"

    async def get_all(self, user_id: int, token: str) -> Optional[list[dict]] | dict:
        url = f"{self.base_url}/list?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /materials/list → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logging.error(f"[API] Error: {await response.text()}")
                return None

    async def get_by_id(self, user_id: int, material_id: int, token: str) -> Optional[dict] | dict:
        url = f"{self.base_url}/{material_id}?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /materials/{material_id} → {response.status}")
                if response.status == 200:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logging.error(f"[API] Error: {await response.text()}")
                return None

    async def add(self, request: MaterialCreateRequest) -> Optional[dict] | dict:
        url = f"{self.base_url}/add"
        headers = {
            "Authorization": f"Bearer {request.token}",
            "Content-Type": "application/json"
        }

        data = request.model_dump()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                logging.info(f"[API] POST /materials/add → {response.status}")
                if response.status == 201:
                    return await response.json()
                elif response.status == 401:
                    return {"error": "token_expired"}
                logging.error(f"[API] Error: {await response.text()}")
                return None


# async def get_materials_list_api(user_id: int, token: str) -> dict | None:
#     """Получить список всех материалов через"""
#     url = f"{BASE_URL}/list?user_id={user_id}"
#     headers = {"Authorization": f"Bearer {token}"}
#
#
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, headers=headers) as response:
#             logging.info(f"Get materials response status: {response.status}")
#             if response.status == 200:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"Get materials error response: {await response.text()}")
#                 return None
#
# async def get_materials_by_id_api(user_id: int, material_id: int, token: str) -> dict | None:
#     """Получить конкретный материал по ID через API"""
#     url = f"{BASE_URL}/{material_id}?user_id={user_id}"
#     headers = {"Authorization": f"Bearer {token}"}
#
#     async with aiohttp.ClientSession() as session:
#         async with session.get(url, headers=headers) as response:
#             logging.info(f"Get material {material_id} response status: {response.status}")
#             if response.status == 200:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"Get material {material_id} error response: {await response.text()}")
#                 return None
#
# async def add_material_api(material_data: MaterialCreateRequest) -> dict | None:
#     """Добавить новый материал через API"""
#     url = f"{BASE_URL}/add"
#     token = str(material_data.token)
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Content-Type": "application/json"
#     }
#     data = {
#         "user_id": material_data.user_id,
#         "title": material_data.title,
#         "description": material_data.description,
#         "file_url": material_data.file_url,
#         "token": token
#     }
#
#     async with aiohttp.ClientSession() as session:
#         async with session.post(url, json=data, headers=headers) as response:
#             logging.info(f"Add material response status: {response.status}")
#             if response.status == 201:
#                 return await response.json()
#             elif response.status == 401:
#                 return {"error": "token_expired"}
#             else:
#                 logging.error(f"Add material error response: {await response.text()}")
#                 return None