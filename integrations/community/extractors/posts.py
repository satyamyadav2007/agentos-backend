import httpx
from datetime import datetime
from integrations.community.models.post import CommunityPostModel

class CommunityExtractor:
    def __init__(self, api_key: str, domain: str):
        self.api_key = api_key
        self.base_url = f"https://{domain.rstrip('/')}"
        self.headers = {"Api-Key": self.api_key, "Content-Type": "application/json"}

    async def fetch_recent_discussions(self, limit: int = 30) -> list[CommunityPostModel]:
        print(f"🗣️ [Community] Fetching trending forum discussions from {self.base_url}...")
        # Mocking a Discourse-style API endpoint
        endpoint = f"{self.base_url}/latest.json"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(endpoint, headers=self.headers)
                response.raise_for_status()
                topics = response.json().get("topic_list", {}).get("topics", [])
                
                posts = []
                for t in topics[:limit]:
                    posts.append(CommunityPostModel(
                        id=str(t["id"]),
                        topic_id=str(t["id"]),
                        title=t.get("title", ""),
                        content=t.get("excerpt", ""), # Snippet of the discussion
                        author_username=t.get("last_poster_username", "unknown"),
                        created_at=datetime.fromisoformat(t.get("created_at", "").replace('Z', '+00:00')),
                        views=t.get("views", 0),
                        reply_count=t.get("reply_count", 0),
                        tags=t.get("tags", [])
                    ))
                return posts
        except Exception as e:
            print(f"🚨 [Community Extractor] Failed: {e}")
            return []