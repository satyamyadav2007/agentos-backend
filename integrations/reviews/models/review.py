from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class AppReviewModel(BaseModel):
    id: str
    provider: str  # 'appstore', 'googleplay', 'chrome'
    app_id: str
    title: str
    body: str
    rating: int    # 1 to 5
    version: Optional[str] = "unknown"
    country: Optional[str] = "global"
    language: Optional[str] = "en"
    created_at: datetime

    @property
    def is_critical_regression(self) -> bool:
        """AI Heuristic: 1 or 2 star review containing bug/crash keywords."""
        if self.rating > 2:
            return False
        
        urgent_keywords = ["crash", "broken", "update", "worst", "bug", "stuck", "login", "blank"]
        content = f"{self.title} {self.body}".lower()
        return any(keyword in content for keyword in urgent_keywords)