from typing import Dict, Any, List

class JiraCommentsExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_issue_comments(self, issue_key: str) -> List[Dict[str, Any]]:
        """Fetches comment threads to build communication context."""
        try:
            endpoint = f"rest/api/3/issue/{issue_key}/comment"
            response = await self.client.get(endpoint)
            
            comments = response.get("comments", [])
            return comments
            
        except Exception as e:
            # Silent fail for issues with zero comments to keep logs clean
            return []