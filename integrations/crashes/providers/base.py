from abc import ABC, abstractmethod
from typing import List, Dict, Any
from integrations.crashes.models.crash import CrashModel

class BaseCrashProvider(ABC):
    """Abstract Base Class for Crash/Exception Intelligence (Sentry, Crashlytics)."""
    
    def __init__(self, api_key: str, organization_slug: str, project_slug: str):
        self.api_key = api_key
        self.org_slug = organization_slug
        self.project_slug = project_slug

    @abstractmethod
    async def fetch_unresolved_crashes(self, limit: int = 50) -> List[CrashModel]:
        """Module 3: Crash Intelligence - Fetch active issues."""
        pass

    @abstractmethod
    async def fetch_crash_events(self, issue_id: str) -> Dict[str, Any]:
        """Module 4: Fetch detailed stack traces for a specific issue."""
        pass