from typing import List
from datetime import datetime
from integrations.teams.models.message import TeamsMessageModel, TeamsUserModel

class TeamsMessageExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_channel_messages(self, team_id: str, channel_id: str, limit: int = 50) -> List[TeamsMessageModel]:
        print(f"🏢 [Teams Extractor] Fetching enterprise messages from Channel: {channel_id}...")
        try:
            # Endpoint to get channel messages (Requires ChannelMessage.Read.All scope)
            endpoint = f"teams/{team_id}/channels/{channel_id}/messages"
            params = {"$top": limit, "$orderby": "createdDateTime desc"}
            
            raw_data = await self.client.get(endpoint, params=params)
            messages_data = raw_data.get("value", [])
            
            messages = []
            for msg in messages_data:
                # Strip HTML from Teams message body (Graph API usually returns HTML for rich text)
                raw_content = msg.get("body", {}).get("content", "")
                
                # Extract author info safely
                from_user = msg.get("from", {}).get("user", {})
                author = TeamsUserModel(
                    id=from_user.get("id", "system"),
                    display_name=from_user.get("displayName", "System"),
                    email=from_user.get("email")
                )
                
                messages.append(TeamsMessageModel(
                    id=msg.get("id"),
                    team_id=team_id,
                    channel_id=channel_id,
                    author=author,
                    content=raw_content,
                    created_datetime=datetime.fromisoformat(msg.get("createdDateTime", "").replace('Z', '+00:00')),
                    mentions=[m.get("mentionText") for m in msg.get("mentions", [])],
                    has_attachments=len(msg.get("attachments", [])) > 0,
                    reply_to_id=msg.get("replyToId")
                ))
            
            print(f"   ✅ Extracted {len(messages)} Teams messages.")
            return messages
            
        except Exception as e:
            print(f"🚨 [Teams Extractor] Failed to fetch messages: {e}")
            return []