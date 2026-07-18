import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class SlackIncidentService:
    def __init__(self, client):
        self.client = client
        # Keywords that indicate a system issue or incident
        self.incident_keywords = ["outage", "sev1", "sev-1", "sev2", "crash", "down", "rollback", "incident"]

    async def detect_active_incidents(self, channel_id: str, channel_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Scans recent messages for incident keywords and fetches their entire thread context."""
        print(f"🚨 [Incident Service] Scanning #{channel_name} for anomalies...")
        detected_incidents = []
        
        try:
            history_res = await self.client.get("conversations.history", params={"channel": channel_id, "limit": limit})
            messages = history_res.get("messages", [])
            
            for msg in messages:
                text = msg.get("text", "").lower()
                
                # Check if message contains any critical keywords
                if any(keyword in text for keyword in self.incident_keywords):
                    incident_data = {
                        "type": "incident_alert",
                        "channel": channel_name,
                        "timestamp": msg.get("ts"),
                        "text": msg.get("text"),
                        "author_id": msg.get("user"),
                        "thread_replies": []
                    }
                    
                    # If the incident alert sparked a discussion, fetch the thread!
                    thread_ts = msg.get("thread_ts")
                    if thread_ts and int(msg.get("reply_count", 0)) > 0:
                        thread_res = await self.client.get("conversations.replies", params={"channel": channel_id, "ts": thread_ts})
                        replies = thread_res.get("messages", [])
                        # Skip the first message as it's the parent we already have
                        incident_data["thread_replies"] = [r.get("text") for r in replies[1:] if r.get("type") == "message"]
                    
                    detected_incidents.append(incident_data)
                    
            return detected_incidents
            
        except Exception as e:
            logger.error(f"Failed to detect incidents in {channel_name}: {e}")
            return []