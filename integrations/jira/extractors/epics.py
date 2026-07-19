from typing import Dict, Any, List

class JiraEpicsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_epics(self, project_key: str) -> list:
        print(f"🏔️ [Jira Extractor] Fetching Epics for Project: {project_key}...")
        
        jql_query = f'project="{project_key}" AND issuetype=Epic ORDER BY created DESC'
        
        # ⚡ FIX: POST request demands fields as a list of strings
        payload = {
            "jql": jql_query,
            "maxResults": 50,
            "fields": ["summary", "description", "status", "priority", "assignee", "created", "updated"]
        }
        
        try:
            # ⚡ FIX: Migrated to the new /search/jql endpoint as per Atlassian's requirement
            response = await self.client.post("rest/api/3/search/jql", json_data=payload)
            
            epics = response.get("issues", []) if response else []
            print(f"   ✅ Extracted {len(epics)} Epics from {project_key}")
            return epics
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching epics for {project_key}: {e}")
            return []