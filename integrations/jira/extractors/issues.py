from typing import Dict, Any, List

class JiraIssuesExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_issues(self, project_key: str) -> List[Dict[str, Any]]:
        print(f"🐛 [Jira Extractor] Fetching issues for Project: {project_key}...")
        
        # JQL: Fetching all standard issues (Task, Bug, Story), excluding Epics
        jql_query = f'project="{project_key}" AND issuetype != Epic ORDER BY updated DESC'
        
        # ⚡ FIX: Passing parameters directly for the GET request
        params = {
            "jql": jql_query,
            "maxResults": 100, # Ek baar mein 100 issues layega (tum isko badha/ghata sakte ho)
            "fields": "summary,description,status,issuetype,priority,assignee,created,updated" 
        }
        
        try:
            # ⚡ FIX: Changed self.client.post to self.client.get
            response = await self.client.get("rest/api/3/search", params=params)
            
            # Ensure safe extraction
            issues = response.get("issues", []) if response else []
            print(f"   ✅ Extracted {len(issues)} issues from {project_key}")
            return issues
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching issues for {project_key}: {e}")
            return []