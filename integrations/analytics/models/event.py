from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AnalyticsEventModel(BaseModel):
    id: str
    provider: str  # 'mixpanel', 'amplitude', 'posthog'
    event_name: str
    user_id: str
    timestamp: datetime
    properties: Dict[str, Any] = {}
    
    # Advanced features (PostHog / Amplitude)
    session_id: Optional[str] = None
    feature_flag_active: Optional[bool] = None
    current_url: Optional[str] = None

    @property
    def is_dropoff_signal(self) -> bool:
        """AI Heuristic: Detects if this event suggests user abandonment."""
        return self.event_name.lower() in ["error", "exit", "bounce", "payment_failed"]