from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class TeamsUserModel(BaseModel):
    id: str
    display_name: str
    email: Optional[str] = None

class TeamsMessageModel(BaseModel):
    id: str
    team_id: str
    channel_id: str
    author: TeamsUserModel
    content: str
    created_datetime: datetime
    last_modified_datetime: Optional[datetime] = None
    mentions: List[str] = []
    has_attachments: bool = False
    reply_to_id: Optional[str] = None # For thread mapping

    @property
    def is_escalation(self) -> bool:
        """AI Heuristic: Detects urgency in enterprise chat."""
        urgency_keywords = ["urgent", "blocker", "incident", "p0", "escalation", "customer down"]
        return any(keyword in self.content.lower() for keyword in urgency_keywords)