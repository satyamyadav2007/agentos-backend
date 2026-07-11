from typing import List
from integrations.intercom.models.conversation import IntercomConversationModel

class IntercomConversationExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_active_conversations(self) -> List[IntercomConversationModel]:
        print("💬 [Intercom Extractor] Fetching active customer conversations...")
        try:
            # Fetching open conversations for immediate AI processing
            raw_data = await self.client.get("conversations", params={"state": "open"})
            conversations_data = raw_data.get("conversations", [])
            
            conversations = [IntercomConversationModel(**item) for item in conversations_data]
            print(f"   ✅ Extracted {len(conversations)} Active Conversations.")
            return conversations
        except Exception as e:
            print(f"🚨 [Intercom Extractor] Failed to fetch conversations: {e}")
            return []