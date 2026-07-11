from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DatadogEventModel(BaseModel):
    id: str
    title: str
    text: str
    alert_type: str  # error, warning, info, success
    priority: str    # normal, low
    source_type_name: str # e.g., github, jenkins, kubernetes, monitor
    tags: List[str] = []
    host: Optional[str] = None
    date_happened: datetime

    @property
    def is_critical_incident(self) -> bool:
        """AI Heuristic: Detects critical production issues from tags and text."""
        critical_tags = ["env:production", "env:prod", "severity:critical"]
        is_prod = any(tag in self.tags for tag in critical_tags)
        is_error = self.alert_type == "error"
        return is_prod and is_error