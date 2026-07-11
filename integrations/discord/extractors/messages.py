from typing import List
from integrations.discord.models.message import DiscordMessageModel

class DiscordMessageExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_messages(self, channel_id: str, limit: int = 100) -> List[DiscordMessageModel]:
        print(f"💬 [Discord Extractor] Fetching community messages from channel {channel_id}...")
        try:
            raw_data = await self.client.get(
                f"channels/{channel_id}/messages", 
                params={"limit": limit}
            )
            
            # Discord API returns a list directly
            messages = [DiscordMessageModel(**item) for item in raw_data if not item.get("author", {}).get("bot")]
            
            print(f"   ✅ Extracted {len(messages)} human messages/forum posts.")
            return messages
        except Exception as e:
            print(f"🚨 [Discord Extractor] Failed to fetch messages: {e}")
            return []