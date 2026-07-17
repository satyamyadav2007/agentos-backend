from typing import Dict, Any, List

class JiraSprintExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_active_sprints(self, board_id: int) -> List[Dict[str, Any]]:
        """Fetches active sprints for a given Agile Board using the Agile API."""
        print(f"🏃 [Jira Extractor] Scanning sprints for Board ID: {board_id}...")
        
        try:
            # ⚡ FIX: Explicitly using the Agile API path without the relative '../' hack
            endpoint = f"rest/agile/1.0/board/{board_id}/sprint?state=active"
            response = await self.client.get(endpoint)
            
            # Since client now returns {} on failure (like 404 for Kanban boards), it won't crash
            sprints = response.get("values", [])
            print(f"   ✅ Found {len(sprints)} active sprints on Board {board_id}")
            return sprints
            
        except Exception as e:
            print(f"⚠️ [Jira Extractor] Could not fetch sprints for Board {board_id}: {e}")
            return []