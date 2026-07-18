from typing import Dict, Any, List

class JiraIssuesExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_issues(self, project_key: str) -> List[Dict[str, Any]]:
        """Fetches issues for a specific Jira project using the standard v3 API."""
        print(f"🐛 [Jira Extractor] Fetching issues for Project: {project_key}...")
        
        # ⚡ FIX: Added standard JQL for issues
        jql_query = f'project="{project_key}" ORDER BY created DESC'
        
        # ⚡ FIX: Merged all fields into a single comma-separated string required by the API
        params = {
            "jql": jql_query,
            "maxResults": 100,
            "fields": "summary,description,issuetype,status,priority,assignee,creator,created,updated"
        }
        
        print(f"🔍 [Debug] Issues Endpoint URL: rest/api/3/search")
        print(f"🔍 [Debug] Issues Params: {params}")
        
        try:
            response = await self.client.get("rest/api/3/search", params=params)
            
            # Safe extraction assuming client returns {} on error
            issues = response.get("issues", []) if response else []
            
            print(f"   ✅ Extracted {len(issues)} issues from {project_key}")
            return issues
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching issues for {project_key}: {e}")
            return []