from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class SpeakerModel(BaseModel):
    id: str
    name: str
    role: str = "unknown" # 'customer', 'sales', 'engineering'
    talk_ratio: Optional[float] = None

class ConversationCallModel(BaseModel):
    id: str
    provider: str  # 'gong', 'fireflies', 'otter'
    title: str
    workspace_id: str
    start_time: datetime
    duration_minutes: int
    speakers: List[SpeakerModel] = []
    
    # Transcript & Insights
    transcript_text: str = ""
    summary: Optional[str] = None
    action_items: List[str] = []
    
    # Revenue & Deal Context
    deal_id: Optional[str] = None # Maps to Salesforce Opportunity
    primary_objection: Optional[str] = None
    churn_risk_detected: bool = False

    @property
    def is_revenue_critical(self) -> bool:
        """AI Heuristic: Flags calls that mention pricing, competitors, or cancellations."""
        keywords = ["expensive", "competitor", "cancel", "renewal", "discount", "blocker"]
        content = self.transcript_text.lower()
        return any(k in content for k in keywords) or self.churn_risk_detected