import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SlackConversationService:
    def __init__(self, client):
        self.client = client

    async def extract_deep_discussions(self, channel_id: str, channel_name: str, min_replies: int = 5) -> List[Dict[str, Any]]:
        """Finds highly engaged threads (potential feature requests or customer pain points)."""
        print(f"💬 [Conversation Service] Analyzing engagement in #{channel_name}...")
        deep_conversations = []
        
        try:
            # Fetch recent history
            history_res = await self.client.get("conversations.history", params={"channel": channel_id, "limit": 100})
            messages = history_res.get("messages", [])
            
            for msg in messages:
                reply_count = int(msg.get("reply_count", 0))
                
                # If a message has a lot of replies, it's a hot topic!
                if reply_count >= min_replies and msg.get("thread_ts"):
                    thread_ts = msg.get("thread_ts")
                    
                    # Fetch the full conversation
                    thread_res = await self.client.get("conversations.replies", params={"channel": channel_id, "ts": thread_ts})
                    replies = thread_res.get("messages", [])
                    
                    participants = set(r.get("user") for r in replies if r.get("user"))
                    
                    conversation_data = {
                        "type": "deep_discussion",
                        "channel": channel_name,
                        "topic": msg.get("text"),
                        "reply_count": reply_count,
                        "unique_participants": len(participants),
                        "full_thread": [r.get("text") for r in replies if r.get("type") == "message"]
                    }
                    
                    deep_conversations.append(conversation_data)
                    
            return deep_conversations
            
        except Exception as e:
            logger.error(f"Failed to extract conversations in {channel_name}: {e}")
            return []