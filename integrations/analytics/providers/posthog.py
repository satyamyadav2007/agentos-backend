import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseAnalyticsProvider
from ..models.event import AnalyticsEventModel

class PostHogProvider(BaseAnalyticsProvider):
    """PostHog implementation of the unified analytics engine."""
    
    def __init__(self, api_key: str, project_id: str, host: str = "https://app.posthog.com"):
        super().__init__(api_key, project_id)
        self.base_url = f"{host}/api/projects/{project_id}"
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    async def fetch_recent_events(self, limit: int = 100) -> List[AnalyticsEventModel]:
        print(f"📊 [PostHog Provider] Fetching latest user events...")
        url = f"{self.base_url}/events/"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params={"limit": limit})
            response.raise_for_status()
            raw_events = response.json().get("results", [])
            
            standardized_events = []
            for ev in raw_events:
                props = ev.get("properties", {})
                standardized_events.append(
                    AnalyticsEventModel(
                        id=ev.get("id"),
                        provider="posthog",
                        event_name=ev.get("event"),
                        user_id=ev.get("distinct_id"),
                        timestamp=datetime.fromisoformat(ev.get("timestamp").replace('Z', '+00:00')),
                        properties=props,
                        session_id=props.get("$session_id"),
                        current_url=props.get("$current_url")
                    )
                )
            print(f"   ✅ Standardized {len(standardized_events)} PostHog events.")
            return standardized_events

    async def fetch_funnel_dropoffs(self, funnel_id: str) -> Dict[str, Any]:
        # Implementation for pulling funnel stats
        pass