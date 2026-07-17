from typing import Dict, Any, List

class JiraEpicsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_epics(self, project_key: str) -> List[Dict[str, Any]]:
        """Fetches all Epics for a specific project to map strategic initiatives."""
        print(f"🏔️ [Jira Extractor] Fetching Epics for Project: {project_key}...")
        
        jql_query = f'project="{project_key}" AND issuetype=Epic ORDER BY created DESC'
        payload = {
            "jql": jql_query,
            "maxResults": 50, # Epics are usually fewer than standard issues
            "fields": ["summary", "description", "status", "priority", "assignee"] 
        }
        
        try:
            response = await self.client.post("rest/api/3/search", json_data=payload)
            epics = response.get("issues", [])
            
            print(f"   ✅ Extracted {len(epics)} Epics from {project_key}")
            return epics
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching epics for {project_key}: {e}")
            return []