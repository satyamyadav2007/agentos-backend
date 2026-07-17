from typing import Dict, Any, List, Optional

class JiraBoardsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_boards(self, project_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetches Agile boards, optionally filtered by project key."""
        log_msg = f" for Project: {project_key}" if project_key else " across workspace"
        print(f"📋 [Jira Extractor] Fetching Agile boards{log_msg}...")
        
        try:
            endpoint = "rest/agile/1.0/board"
            params = {"projectKeyOrId": project_key} if project_key else None
            
            response = await self.client.get(endpoint, params=params)
            boards = response.get("values", [])
            
            print(f"   ✅ Found {len(boards)} agile boards.")
            return boards
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching boards: {e}")
            return []