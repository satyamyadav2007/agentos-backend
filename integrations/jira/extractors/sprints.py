from typing import Dict, Any, List

class JiraSprintExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_active_sprints(self, board_id: int) -> List[Dict[str, Any]]:
        """Fetches active sprints for a given Agile Board."""
        print(f"🏃 [Jira Extractor] Scanning sprints for Board ID: {board_id}...")
        
        try:
            # Note: Sprints use the Agile API, which is slightly different from v3, 
            # but routed through the same base URL in Atlassian 3LO
            endpoint = f"../agile/1.0/board/{board_id}/sprint?state=active"
            response = await self.client.get(endpoint)
            
            sprints = response.get("values", [])
            print(f"   ✅ Found {len(sprints)} active sprints on Board {board_id}")
            return sprints
        except Exception as e:
            # Board might not support sprints (e.g., Kanban boards)
            print(f"⚠️ [Jira Extractor] Could not fetch sprints for Board {board_id}. (Might be Kanban)")
            return []