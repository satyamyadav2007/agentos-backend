import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseCrashProvider
from ..models.crash import CrashModel

class SentryProvider(BaseCrashProvider):
    """Sentry implementation of the unified crash engine."""
    
    def __init__(self, api_key: str, organization_slug: str, project_slug: str):
        super().__init__(api_key, organization_slug, project_slug)
        self.base_url = "https://sentry.io/api/0"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def fetch_unresolved_crashes(self, limit: int = 50) -> List[CrashModel]:
        print(f"🔥 [Sentry Provider] Fetching unresolved backend/frontend crashes...")
        url = f"{self.base_url}/projects/{self.org_slug}/{self.project_slug}/issues/"
        
        # Only fetch unresolved issues to focus AI on current problems
        params = {"query": "is:unresolved", "limit": limit}
        
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            raw_issues = response.json()
            
            standardized_crashes = []
            for issue in raw_issues:
                standardized_crashes.append(
                    CrashModel(
                        id=str(issue.get("id")),
                        provider="sentry",
                        project_id=self.project_slug,
                        title=issue.get("title", "Unknown Crash"),
                        culprit=issue.get("culprit"),
                        release_version=issue.get("firstRelease", {}).get("version"),
                        user_count=issue.get("count", 0), # Sentry usually tracks total events, users might be separate
                        event_count=int(issue.get("count", 0)),
                        first_seen=datetime.fromisoformat(issue.get("firstSeen", "").replace('Z', '+00:00')),
                        last_seen=datetime.fromisoformat(issue.get("lastSeen", "").replace('Z', '+00:00')),
                        metadata={"sentry_type": issue.get("type"), "level": issue.get("level")}
                    )
                )
            print(f"   ✅ Standardized {len(standardized_crashes)} Sentry crashes.")
            return standardized_crashes

    async def fetch_crash_events(self, issue_id: str) -> Dict[str, Any]:
        # Logic to fetch exact stack trace for Root Cause Analysis
        pass