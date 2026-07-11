from typing import List
from datetime import datetime
from integrations.datadog.models.monitor import DatadogEventModel

class DatadogMonitorExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_recent_alerts(self, limit: int = 30) -> List[DatadogEventModel]:
        print(f"📈 [Datadog Extractor] Fetching recent infrastructure & APM alerts...")
        
        # Fetching events from Datadog API
        try:
            raw_data = await self.client.get("events")
            events_data = raw_data.get("events", [])
            
            alerts = []
            for e in events_data[:limit]:
                alerts.append(DatadogEventModel(
                    id=str(e.get("id")),
                    title=e.get("title", "No Title"),
                    text=e.get("text", ""),
                    alert_type=e.get("alert_type", "info"),
                    priority=e.get("priority", "normal"),
                    source_type_name=e.get("source_type_name", "monitor"),
                    tags=e.get("tags", []),
                    host=e.get("host"),
                    date_happened=datetime.fromtimestamp(e.get("date_happened", 0))
                ))
            
            print(f"   ✅ Extracted {len(alerts)} Datadog alerts.")
            return alerts
            
        except Exception as e:
            print(f"🚨 [Datadog Extractor] Failed to fetch alerts: {e}")
            return []