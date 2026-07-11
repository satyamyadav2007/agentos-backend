from typing import Dict, Any, List
from integrations.intercom.extractors.conversations import IntercomConversationExtractor
from integrations.intercom.normalizer import IntercomNormalizer

class IntercomSyncService:
    """Orchestrates extraction and normalization for Intercom Conversational Data."""
    
    def __init__(self, client):
        self.client = client
        self.conversation_extractor = IntercomConversationExtractor(client)
        # self.contact_extractor = IntercomContactExtractor(client) -> Coming soon
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Intercom Sync] Starting Conversational Intelligence Sync...")
        
        all_universal_events = []
        
        # 1. Fetch Conversations
        conversations_models = await self.conversation_extractor.fetch_active_conversations()
        
        # 2. Normalize to Universal Format
        for convo in conversations_models:
            normalized = IntercomNormalizer.normalize_conversation(convo)
            all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} chat entities from Intercom!")
        return all_universal_events