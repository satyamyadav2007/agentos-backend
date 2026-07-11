from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from ..models.review import AppReviewModel

class BaseReviewProvider(ABC):
    """Abstract Base Class for all Public Product Feedback Providers."""
    
    @abstractmethod
    async def fetch_recent_reviews(self, limit: int = 50) -> List[AppReviewModel]:
        """
        Fetches recent reviews from the respective platform.
        Must be implemented by all specific provider classes (App Store, Play Store, Chrome, etc.).
        """
        pass