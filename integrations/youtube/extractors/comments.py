from typing import List
from integrations.youtube.models.comment import YouTubeCommentModel

class YouTubeCommentExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_video_comments(self, video_id: str, limit: int = 100) -> List[YouTubeCommentModel]:
        print(f"▶️ [YouTube Extractor] Fetching comments for Video ID: '{video_id}'...")
        try:
            params = {
                "part": "snippet",
                "videoId": video_id,
                "maxResults": min(limit, 100), # YouTube max is 100 per page
                "order": "relevance" # Gets the most liked/engaged comments first
            }
            raw_data = await self.client.get("commentThreads", params=params)
            
            items = raw_data.get("items", [])
            comments = [YouTubeCommentModel.from_youtube_response(item) for item in items]
            
            print(f"   ✅ Extracted {len(comments)} top comments from video {video_id}.")
            return comments
            
        except Exception as e:
            print(f"🚨 [YouTube Extractor] Failed to fetch comments: {e}")
            return []