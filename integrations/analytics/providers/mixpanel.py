import httpx
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Any
from .base import BaseAnalyticsProvider
from ..models.event import AnalyticsEventModel

class MixpanelProvider(BaseAnalyticsProvider):
    """Mixpanel implementation of the unified analytics engine."""
    
    def __init__(self, api_key: str, project_id: str, host: str = "https://data.mixpanel.com/api/2.0"):
        # For Mixpanel, api_key usually represents the Service Account Secret or Project Secret
        super().__init__(api_key, project_id)
        self.base_url = host
        
        # Mixpanel uses Basic Auth
        auth_string = f"{self.api_key}:" # Sometimes it's secret: (empty password)
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        self.headers = {"Authorization": f"Basic {encoded_auth}", "Accept": "application/json"}

    async def fetch_recent_events(self, limit: int = 100) -> List[AnalyticsEventModel]:
        print(f"📊 [Mixpanel Provider] Fetching latest user events...")
        url = f"{self.base_url}/export"
        
        # Mixpanel export requires from_date and to_date
        today = datetime.utcnow()
        from_date = (today - timedelta(days=1)).strftime('%Y-%m-%d')
        to_date = today.strftime('%Y-%m-%d')
        
        params = {
            "from_date": from_date,
            "to_date": to_date,
            "limit": limit
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            
            # Mixpanel export returns JSON lines (NDJSON), not a standard JSON array
            raw_lines = response.text.strip().split('\n')
            import json
            raw_events = [json.loads(line) for line in raw_lines if line]
            
            standardized_events = []
            for ev in raw_events:
                props = ev.get("properties", {})
                standardized_events.append(
                    AnalyticsEventModel(
                        id=props.get("$insert_id", str(ev.get("event"))),
                        provider="mixpanel",
                        event_name=ev.get("event"),
                        user_id=props.get("distinct_id", "anonymous"),
                        timestamp=datetime.fromtimestamp(props.get("time", 0)),
                        properties=props,
                        session_id=props.get("$session_id"),
                        current_url=props.get("$current_url")
                    )
                )
            print(f"   ✅ Standardized {len(standardized_events)} Mixpanel events.")
            return standardized_events

    async def fetch_funnel_dropoffs(self, funnel_id: str) -> Dict[str, Any]:
        pass