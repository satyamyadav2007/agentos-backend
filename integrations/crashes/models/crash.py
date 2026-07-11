from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class CrashModel(BaseModel):
    id: str
    provider: str  # 'sentry' or 'crashlytics'
    project_id: str
    title: str  # e.g., "NullPointerException in PaymentController"
    culprit: Optional[str] = None  # The specific file/function
    release_version: Optional[str] = None
    environment: Optional[str] = "production"
    
    # Impact Metrics
    user_count: int = 0
    event_count: int = 0
    
    first_seen: datetime
    last_seen: datetime
    
    # Detailed Trace (For AI Root Cause Analysis)
    stack_trace_snippet: Optional[str] = None
    metadata: Dict[str, Any] = {}

    @property
    def is_critical(self) -> bool:
        """AI Heuristic: Critical if it affects many users or is a core backend failure."""
        return self.user_count > 50 or "payment" in self.title.lower() or "auth" in self.title.lower()