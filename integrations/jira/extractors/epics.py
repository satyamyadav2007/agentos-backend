from typing import Dict, Any, List

class JiraEpicsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_epics(self, project_key: str) -> list:
        print(f"🏔️ [Jira Extractor] Fetching Epics for Project: {project_key}...")
        
        jql_query = f'project="{project_key}" AND issuetype=Epic ORDER BY created DESC'
        
        params = {
            "jql": jql_query,
            "maxResults": 50,
            "fields": "summary,description,status,priority,assignee,created,updated" 
        }
        
        try:
            response = await self.client.get("rest/api/3/search", params=params)
            
            epics = response.get("issues", []) if response else []
            print(f"   ✅ Extracted {len(epics)} Epics from {project_key}")
            return epics
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching epics for {project_key}: {e}")
            return []