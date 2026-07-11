from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class TwitterUserModel(BaseModel):
    id: str
    username: str
    follower_count: int = 0

class TweetModel(BaseModel):
    id: str
    text: str
    author: TwitterUserModel
    created_at: datetime
    retweet_count: int = 0
    like_count: int = 0
    reply_count: int = 0

    @property
    def is_viral_or_urgent(self) -> bool:
        """AI Heuristic: Detects if the tweet is an outage alert or going viral."""
        urgent_keywords = ["outage", "down", "broken", "failing", "error", "worst", "fix"]
        has_urgent_word = any(word in self.text.lower() for word in urgent_keywords)
        is_gaining_traction = self.retweet_count > 20 or self.like_count > 50
        
        # If a big account complains, or if it has urgent keywords, it's a crisis signal
        return has_urgent_word or is_gaining_traction or self.author.follower_count > 10000