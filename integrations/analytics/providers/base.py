from abc import ABC, abstractmethod
from typing import Optional
from typing import List, Dict, Any
from integrations.analytics.models.event import AnalyticsEventModel

class BaseAnalyticsProvider(ABC):
    """Abstract Base Class for all Analytics Providers (Mixpanel, PostHog, Amplitude)."""
    
    def __init__(self, api_key: str, project_id: Optional[str] = None):
        self.api_key = api_key
        self.project_id = project_id

    @abstractmethod
    async def fetch_recent_events(self, limit: int = 100) -> List[AnalyticsEventModel]:
        pass

    @abstractmethod
    async def fetch_funnel_dropoffs(self, funnel_id: str) -> Dict[str, Any]:
        """Module 5: Funnel Intelligence"""
        pass