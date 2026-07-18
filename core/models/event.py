from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

class UniversalEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source: str       
    entity_type: str  
    repository: str   
    title: str
    description: str
    author: str
    severity: str     
    timestamp: datetime
    
    revenue_risk: Optional[float] = 0.0
    engagement_score: float = 0.0
    
    metadata: Dict[str, Any] = {}
    linked_entities: List[str] = []