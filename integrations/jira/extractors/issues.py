from typing import Dict, Any, List

class JiraIssuesExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_issues(self, project_key: str) -> List[Dict[str, Any]]:
        """Fetches issues for a specific Jira project."""
        print(f"🐛 [Jira Extractor] Fetching issues for Project: {project_key}...")
        
        # JQL to get all issues for the project (max 100 for now to avoid overload)
        jql_query = f'project="{project_key}" ORDER BY created DESC'
        payload = {
            "jql": jql_query,
            "maxResults": 100,
            "fields": [
                "summary", "description", "issuetype", "status", 
                "priority", "assignee", "creator", "created"
            ]
        }
        
        try:
            # Using the centralized JiraClient's post method for search
            response = await self.client.post("search", json_data=payload)
            issues = response.get("issues", [])
            print(f"   ✅ Extracted {len(issues)} issues from {project_key}")
            return issues
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching issues for {project_key}: {e}")
            return []