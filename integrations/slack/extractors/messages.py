from typing import Dict, Any, List

class SlackMessageExtractor:
    """Module 3: Collects Messages, Threads, Mentions, and Reactions."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_channel_history(self, channel_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Fetches the latest messages from a channel."""
        print(f"💬 [Slack Extractor] Fetching history for channel {channel_id}...")
        try:
            response = await self.client.get(
                "conversations.history", 
                params={"channel": channel_id, "limit": limit}
            )
            return response.get("messages", [])
        except Exception as e:
            print(f"🚨 [Slack Extractor Error]: Could not fetch history. {e}")
            return []

    async def fetch_thread_replies(self, channel_id: str, thread_ts: str) -> List[Dict[str, Any]]:
        """If a message has replies, this fetches the entire thread (Module 12 Prep)."""
        try:
            response = await self.client.get(
                "conversations.replies", 
                params={"channel": channel_id, "ts": thread_ts}
            )
            # Slack returns the parent message + all replies in chronological order
            replies = response.get("messages", [])
            print(f"   🧵 Extracted {len(replies) - 1} replies from thread {thread_ts}")
            return replies
        except Exception as e:
            print(f"🚨 [Slack Extractor Error - Threads]: {e}")
            return []

    def enrich_messages_with_users(self, messages: List[Dict[str, Any]], user_map: Dict[str, str]) -> List[Dict[str, Any]]:
        """Replaces raw Slack User IDs (U12345) with Real Names for the AI."""
        enriched = []
        for msg in messages:
            # Skip system bot messages
            if msg.get("subtype") == "bot_message" or msg.get("bot_id"):
                continue
                
            user_id = msg.get("user")
            msg["real_author_name"] = user_map.get(user_id, "Unknown User")
            enriched.append(msg)
            
        return enriched