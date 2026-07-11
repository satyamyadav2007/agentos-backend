from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class FreshdeskTicketModel(BaseModel):
    id: int
    subject: str
    description_text: Optional[str] = ""
    status: int      # 2: Open, 3: Pending, 4: Resolved, 5: Closed
    priority: int    # 1: Low, 2: Medium, 3: High, 4: Urgent
    requester_id: int
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []

    @property
    def severity_label(self) -> str:
        """Maps Freshdesk priority to AgentOS severity."""
        if self.priority == 4: return "Critical"
        if self.priority == 3: return "High"
        if self.priority == 2: return "Medium"
        return "Low"

    @property
    def is_unresolved(self) -> bool:
        return self.status in [2, 3]