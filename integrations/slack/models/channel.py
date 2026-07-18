from pydantic import BaseModel
from typing import Optional, Dict, Any

class SlackChannel(BaseModel):
    id: str
    name: str
    is_channel: bool = True
    is_group: bool = False
    is_im: bool = False
    created: int
    creator: str
    is_archived: bool = False
    is_general: bool = False
    num_members: Optional[int] = 0
    topic: Optional[Dict[str, Any]] = None
    purpose: Optional[Dict[str, Any]] = None