from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class IntercomContactModel(BaseModel):
    id: str
    role: str # 'user' or 'lead'
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    last_seen_at: Optional[datetime] = None
    signed_up_at: Optional[datetime] = None
    custom_attributes: Dict[str, Any] = {}

    @property
    def is_churn_risk(self) -> bool:
        """Simple baseline logic before AI takes over."""
        # E.g., hasn't been seen in 30 days
        if not self.last_seen_at:
            return True
        return (datetime.now(self.last_seen_at.tzinfo) - self.last_seen_at).days > 30