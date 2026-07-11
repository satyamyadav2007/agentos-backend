from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class RedditPostModel(BaseModel):
    id: str
    subreddit: str
    title: str
    selftext: str  # The actual body of the post
    author: str
    score: int  # Upvotes - Downvotes (Engagement signal)
    num_comments: int
    url: str
    created_utc: datetime
    
    # AI Enriched Fields (Will be populated by Theme & Sentiment Agents)
    sentiment: Optional[str] = "Neutral"
    is_competitor_mention: bool = False

    @property
    def total_engagement(self) -> int:
        """High engagement = High priority for the AI CPO."""
        return self.score + self.num_comments

    @classmethod
    def from_reddit_response(cls, data: Dict[str, Any]):
        """Helper to flatten Reddit's deeply nested 'data' dictionary."""
        post_data = data.get("data", {})
        return cls(
            id=post_data.get("id"),
            subreddit=post_data.get("subreddit"),
            title=post_data.get("title", ""),
            selftext=post_data.get("selftext", ""),
            author=post_data.get("author", "Unknown"),
            score=post_data.get("score", 0),
            num_comments=post_data.get("num_comments", 0),
            url=post_data.get("url", ""),
            created_utc=datetime.fromtimestamp(post_data.get("created_utc", 0))
        )