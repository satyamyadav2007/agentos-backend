import httpx
from typing import Dict, Any, Optional

class DiscordClient:
    """Centralized HTTP Client for Discord API v10."""
    
    def __init__(self, token: str, is_bot: bool = True):
        self.base_url = "https://discord.com/api/v10"
        self.timeout = httpx.Timeout(20.0)
        
        # Discord distinguishes between Bot tokens and OAuth Bearer tokens
        auth_prefix = "Bot" if is_bot else "Bearer"
        self.headers = {
            "Authorization": f"{auth_prefix} {token}",
            "Content-Type": "application/json"
        }

    async def get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()