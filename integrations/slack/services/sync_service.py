from typing import Dict, Any, List
from integrations.slack.normalizer import SlackNormalizer

class SlackSyncService:
    def __init__(self, client):
        self.client = client
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Slack Sync Service] Scanning conversations...")
        
        # 1. Discover Channels
        channels_res = await self.client.get("conversations.list", params={"types": "public_channel"})
        channels = channels_res.get("channels", [])[:5] # Limit to 5 for initial test to avoid overload
        
        all_normalized_events = []
        
        # 2. Extract recent messages per channel
        for channel in channels:
            chan_id = channel["id"]
            chan_name = channel["name"]
            
            history_res = await self.client.get("conversations.history", params={"channel": chan_id, "limit": 20})
            messages = history_res.get("messages", [])
            
            for msg in messages:
                # Ignore bot messages or empty system messages for now
                if msg.get("type") == "message" and not msg.get("bot_id"):
                    normalized = SlackNormalizer.normalize_message(msg, chan_name)
                    all_normalized_events.append(normalized)
                    
        print(f"🧠 [AgentOS Brain] Normalized {len(all_normalized_events)} total messages from Slack!")
        return all_normalized_events