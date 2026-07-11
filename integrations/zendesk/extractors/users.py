from typing import List
from integrations.zendesk.models.user import ZendeskUserModel

class ZendeskUserExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_users(self, role: str = None) -> List[ZendeskUserModel]:
        """Fetch users. Pass role='agent' to get your internal team, or 'end-user' for customers."""
        print(f"👥 [Zendesk Extractor] Scanning users (Role: {role or 'All'})...")
        params = {"role": role} if role else {}
        try:
            raw_data = await self.client.get("users", params=params)
            users = [ZendeskUserModel(**item) for item in raw_data.get("users", [])]
            print(f"   ✅ Extracted {len(users)} users.")
            return users
        except Exception as e:
            print(f"🚨 [Zendesk Extractor] Failed to fetch users: {e}")
            return []