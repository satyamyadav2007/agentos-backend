from typing import Dict, Any, List

class JiraProjectsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_projects(self) -> List[Dict[str, Any]]:
        """Fetches all projects accessible to the authenticated Jira user."""
        print("📂 [Jira Extractor] Fetching authorized projects...")
        
        try:
            # Using standard REST v3 project search
            response = await self.client.get("rest/api/3/project/search")
            
            projects = response.get("values", [])
            print(f"   ✅ Found {len(projects)} projects.")
            return projects
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching projects: {e}")
            return []