from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class CommunityPostModel(BaseModel):
    id: str
    topic_id: str
    title: str
    content: str
    author_username: str
    created_at: datetime
    views: int = 0
    reply_count: int = 0
    tags: List[str] = []

    @property
    def is_trending(self) -> bool:
        """AI Heuristic: Detects if a topic is gaining unusual traction."""
        return self.views > 500 or self.reply_count > 20