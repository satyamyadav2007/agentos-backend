from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class GA4DropoffModel(BaseModel):
    event_name: str
    drop_percentage: float
    active_users_affected: int
    date_detected: datetime
    funnel_step: Optional[str] = None

    @property
    def is_critical_drop(self) -> bool:
        """AI Heuristic: More than 30% drop-off in a key funnel step is critical."""
        return self.drop_percentage > 30.0 and self.active_users_affected > 100