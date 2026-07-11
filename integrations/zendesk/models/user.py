from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class ZendeskUserModel(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    role: str  # Can be 'end-user', 'agent', or 'admin'
    organization_id: Optional[int] = None
    tags: List[str] = []
    user_fields: Dict[str, Any] = {}
    active: bool
    created_at: datetime

    @property
    def is_agent(self) -> bool:
        return self.role in ["agent", "admin"]