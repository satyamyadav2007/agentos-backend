from typing import Dict, Any, List

class JiraIssuesExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_issues(self, project_key: str) -> list:
        print(f"🐛 [Jira Extractor] Fetching issues for Project: {project_key}...")
        
        jql_query = f'project="{project_key}" AND issuetype != Epic ORDER BY updated DESC'
        
        payload = {
            "jql": jql_query,
            "maxResults": 100,
            "fields": ["summary", "description", "status", "issuetype", "priority", "assignee", "created", "updated"]
        }
        
        try:
            # ⚡ FIX: Migrated to the new /search/jql endpoint
            response = await self.client.post("rest/api/3/search/jql", json_data=payload)
            
            issues = response.get("issues", []) if response else []
            print(f"   ✅ Extracted {len(issues)} issues from {project_key}")
            return issues
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching issues for {project_key}: {e}")
            return []