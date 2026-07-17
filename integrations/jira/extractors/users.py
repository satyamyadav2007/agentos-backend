from typing import Dict, Any, List

class JiraUsersExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_all_users(self) -> List[Dict[str, Any]]:
        """Fetches all active users in the Jira workspace for capacity planning."""
        print("👥 [Jira Extractor] Fetching Jira workspace users...")
        
        try:
            endpoint = "rest/api/3/users/search"
            response = await self.client.get(endpoint)
            
            # The user search endpoint usually returns a direct list, not a dict with 'values'
            users = response if isinstance(response, list) else []
            
            print(f"   ✅ Found {len(users)} users in workspace.")
            return users
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching users: {e}")
            return []