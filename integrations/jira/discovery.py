from typing import Dict, Any, List

class JiraDiscovery:
    def __init__(self, client):
        self.client = client  # Yeh hamara central JiraClient hai jo humne pichle step me banaya tha

    async def fetch_projects(self) -> List[Dict[str, Any]]:
        """Fetches all projects from the connected Jira workspace."""
        print("🔍 [Jira Discovery] Scanning for engineering projects...")
        
        try:
            # Jira Cloud API v3 to get all projects
            projects_data = await self.client.get("project")
            
            clean_projects = []
            for project in projects_data:
                proj_info = {
                    "id": project.get("id"),
                    "key": project.get("key"),  # e.g., 'ENG', 'PROD'
                    "name": project.get("name"),
                    "type": project.get("projectTypeKey", "software")
                }
                clean_projects.append(proj_info)
                print(f"   📦 Found Project: {proj_info['name']} (Key: {proj_info['key']})")
                
            return clean_projects
            
        except Exception as e:
            print(f"🚨 [Jira Discovery] Failed to fetch projects: {e}")
            return []