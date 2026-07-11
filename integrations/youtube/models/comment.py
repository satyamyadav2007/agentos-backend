from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class YouTubeCommentModel(BaseModel):
    id: str
    video_id: str
    author_name: str
    text_display: str
    text_original: str
    like_count: int
    reply_count: int
    published_at: datetime
    updated_at: datetime

    # AI Enriched Fields
    sentiment: Optional[str] = "Neutral"
    is_tutorial_failure: bool = False

    @property
    def engagement_score(self) -> int:
        """High likes on a complaint = High community agreement."""
        return self.like_count + (self.reply_count * 2)

    @classmethod
    def from_youtube_response(cls, item: Dict[str, Any]):
        """Helper to flatten YouTube's deeply nested comment structure."""
        snippet = item.get("snippet", {})
        top_comment = snippet.get("topLevelComment", {}).get("snippet", {})
        
        return cls(
            id=item.get("id"),
            video_id=snippet.get("videoId", "Unknown"),
            author_name=top_comment.get("authorDisplayName", "Anonymous"),
            text_display=top_comment.get("textDisplay", ""),
            text_original=top_comment.get("textOriginal", ""),
            like_count=top_comment.get("likeCount", 0),
            reply_count=snippet.get("totalReplyCount", 0),
            published_at=datetime.fromisoformat(top_comment.get("publishedAt", "").replace('Z', '+00:00')),
            updated_at=datetime.fromisoformat(top_comment.get("updatedAt", "").replace('Z', '+00:00'))
        )