from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

class ZendeskCommentModel(BaseModel):
    id: int
    author_id: int
    body: str
    html_body: str
    public: bool  # False means it's an internal note (goldmine for AI!)
    created_at: datetime
    attachments: List[Dict[str, Any]] = []

    @property
    def is_internal_note(self) -> bool:
        return not self.public