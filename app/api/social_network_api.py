import aiohttp
import logging
from app.database.schemas import SocialNetworkOut, SocialNetworkCreateRequest


class SocialNetworkApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/") + "/social_networks"

    async def get_all(self, user_id: int, token: str) -> list[SocialNetworkOut] | dict | None:
        url = f"{self.base_url}/list?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /social_networks/list ➜ {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return [SocialNetworkOut(**item) for item in data]
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return None

    async def get_by_id(self, user_id: int, social_network_id: int, token: str) -> SocialNetworkOut | dict | None:
        url = f"{self.base_url}/{social_network_id}?user_id={user_id}"
        headers = {"Authorization": f"Bearer {token}"}

        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logging.info(f"[API] GET /social_networks/{social_network_id} → {response.status}")
                if response.status == 200:
                    data = await response.json()
                    return SocialNetworkOut(**data)
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return None

    async def add(self, request: SocialNetworkCreateRequest) -> SocialNetworkOut | dict | None:
        url = f"{self.base_url}/add"
        token = request.token
        headers = {
            "Authorization": f"Bearer {token}"
        }

        data = request.model_dump()

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=data) as response:
                logging.info(f"[API] POST /social_networks/add → {response.status}")
                if response.status == 201:
                    data = await response.json()
                    return SocialNetworkOut(**data)
                elif response.status == 401:
                    return {"error": "token_expired"}
                else:
                    logging.error(f"[API] Error: {await response.text()}")
                    return None




