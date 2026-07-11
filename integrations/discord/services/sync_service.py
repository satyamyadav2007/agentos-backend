from typing import Dict, Any, List
from integrations.discord.extractors.messages import DiscordMessageExtractor
from integrations.discord.normalizer import DiscordNormalizer

class DiscordSyncService:
    """Orchestrates extraction and normalization for Discord Community Data."""
    
    def __init__(self, client):
        self.client = client
        self.message_extractor = DiscordMessageExtractor(client)
        
    async def run_full_sync(self, target_channel_ids: List[str]) -> List[Dict[str, Any]]:
        print("\n🚀 [Discord Sync] Starting Community Intelligence Sync...")
        
        all_universal_events = []
        
        for channel_id in target_channel_ids:
            # 1. Fetch Messages per channel
            messages_models = await self.message_extractor.fetch_recent_messages(channel_id)
            
            # 2. Normalize to Universal Format
            for msg in messages_models:
                # Skipping very short messages (e.g., "hi", "lol") to keep AI signal high
                if len(msg.content) > 15: 
                    normalized = DiscordNormalizer.normalize_message(msg)
                    all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} community feedback events from Discord!")
        return all_universal_events