from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ZendeskTicketModel(BaseModel):
    id: int
    subject: str
    description: str
    priority: Optional[str] = "normal"
    status: str
    type: Optional[str] = None
    requester_id: int
    organization_id: Optional[int] = None
    assignee_id: Optional[int] = None
    tags: List[str] = []
    custom_fields: List[Dict[str, Any]] = []
    created_at: datetime
    updated_at: datetime
    
    # AI Enriched Fields (Populated later by Revenue Agent)
    calculated_arr_risk: Optional[float] = 0.0
    customer_tier: Optional[str] = "Free"

    @property
    def is_critical(self) -> bool:
        return self.priority in ["urgent", "high"] or "critical" in self.tags