from typing import Dict, Any, List

class JiraIssuesExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_project_issues(self, project_key: str) -> List[Dict[str, Any]]:
        print(f"🐛 [Jira Extractor] Fetching issues for Project: {project_key}...")
        
        # JQL query string
        jql_query = f'project="{project_key}" ORDER BY created DESC'
        
        # POST request demands fields as an array of strings, not a comma-separated string
        payload = {
            "jql": jql_query,
            "maxResults": 100,
            "fields": [
                "summary", "description", "issuetype", "status", 
                "priority", "assignee", "creator", "created", "updated"
            ]
        }
        
        try:
            # ⚡ FIX: Shifted to POST request as per modern Atlassian standards
            response = await self.client.post("rest/api/3/search", json_data=payload)
            
            issues = response.get("issues", []) if response else []
            print(f"   ✅ Extracted {len(issues)} issues from {project_key}")
            return issues
            
        except Exception as e:
            print(f"🚨 [Jira Extractor] Error fetching issues for {project_key}: {e}")
            return []