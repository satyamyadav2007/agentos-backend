from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SlackMessage(BaseModel):
    type: str = "message"
    user: Optional[str] = None
    text: str
    ts: str # Timestamp (used as ID in Slack)
    team: Optional[str] = None
    channel: Optional[str] = None  # Extractor se inject karenge
    thread_ts: Optional[str] = None # Agar ye kisi thread ka part hai
    reply_count: Optional[int] = 0
    reactions: Optional[List[Dict[str, Any]]] = []
    files: Optional[List[Dict[str, Any]]] = []
    bot_id: Optional[str] = None # Check karne ke liye ki AI toh nahi bola