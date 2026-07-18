from typing import Dict, Any, List

class JiraEpicsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_epics(self, project_key: str) -> List[Dict[str, Any]]:
        """Fetches all Epics for a specific project to map strategic initiatives."""
        print(f"🏔️ [Jira Extractor] Fetching Epics for Project: {project_key}...")
        
        # ⚡ FIX: Added issuetype=Epic and ORDER BY created DESC
        jql_query = f'project="{project_key}" AND issuetype=Epic ORDER BY created DESC'
        
        # ⚡ FIX: Cleaned up dead payload variable and mapped directly to params
        params = {
            "jql": jql_query,
            "maxResults": 50, # Epics are usually fewer than standard issues
            "fields": "summary,description,status,priority,assignee,created,updated"
        }
        
        print(f"🔍 [Debug] Epics Endpoint URL: rest/api/3/search")
        print(f"🔍 [Debug] Epics Params: {params}")
        
        try:
            response = await self.client.get("rest/api/3/search", params=params)
            
            # Safe extraction assuming client returns {} on error
            epics = response.get("issues", []) if response else []
            
            print(f"   ✅ Extracted {len(epics)} Epics from {project_key}")
            return epics
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching epics for {project_key}: {e}")
            return []