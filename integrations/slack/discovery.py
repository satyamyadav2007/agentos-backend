from typing import Dict, Any, List

class SlackDiscovery:
    """Module 2: Automatically detects the Slack Workspace structure."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_channels(self) -> List[Dict[str, Any]]:
        """Fetches all public and private channels the bot has access to."""
        print("🔍 [Slack Discovery] Scanning Workspace Channels...")
        try:
            # types: public_channel, private_channel
            response = await self.client.get(
                "conversations.list", 
                params={"types": "public_channel,private_channel", "exclude_archived": True}
            )
            channels = response.get("channels", [])
            
            clean_channels = []
            for ch in channels:
                chan_data = {
                    "id": ch.get("id"),
                    "name": ch.get("name"),
                    "is_private": ch.get("is_private", False),
                    "purpose": ch.get("purpose", {}).get("value", "")
                }
                clean_channels.append(chan_data)
                print(f"   📺 Found Channel: #{chan_data['name']} (Private: {chan_data['is_private']})")
                
            return clean_channels
        except Exception as e:
            print(f"🚨 [Slack Discovery Error]: {e}")
            return []

    async def fetch_users(self) -> Dict[str, str]:
        """Fetches workspace users and creates a UserID -> Real Name mapping."""
        print("👥 [Slack Discovery] Scanning Workspace Users...")
        try:
            response = await self.client.get("users.list")
            users = response.get("members", [])
            
            user_map = {}
            for u in users:
                if not u.get("deleted") and not u.get("is_bot"):
                    user_map[u["id"]] = u.get("real_name") or u.get("name")
                    
            print(f"   ✅ Mapped {len(user_map)} human users in workspace.")
            return user_map
        except Exception as e:
            print(f"🚨 [Slack Discovery Error - Users]: {e}")
            return {}