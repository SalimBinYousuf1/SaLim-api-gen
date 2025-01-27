import aiohttp
from typing import Dict, Any


class OAuth2Handler:
    def __init__(self):
        self.token: Dict[str, Any] = {}

    async def get_token(
        self, token_url: str, client_id: str, client_secret: str, scope: str
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "scope": scope,
            }
            async with session.post(token_url, data=data) as response:
                response.raise_for_status()
                self.token = await response.json()
                return self.token

    def get_auth_header(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.token.get('access_token', '')}"}
