from typing import List
from integrations.reddit.models.post import RedditPostModel

class RedditSearchExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_product_mentions(self, keyword: str, limit: int = 50) -> List[RedditPostModel]:
        print(f"🔍 [Reddit Extractor] Scanning internet for mentions of: '{keyword}'...")
        try:
            # Searching across all of Reddit for brutally honest feedback
            params = {"q": keyword, "limit": limit, "sort": "new"}
            raw_data = await self.client.get("search", params=params)
            
            posts_data = raw_data.get("data", {}).get("children", [])
            
            posts = [RedditPostModel.from_reddit_response(item) for item in posts_data]
            print(f"   ✅ Extracted {len(posts)} unfiltered posts about '{keyword}'.")
            return posts
            
        except Exception as e:
            print(f"🚨 [Reddit Extractor] Failed to fetch search results: {e}")
            return []