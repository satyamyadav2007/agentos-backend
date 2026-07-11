from typing import Dict, Any

class ZoomWebhookHandler:
    def __init__(self):
        print("🕸️ [Zoom Webhook] Initialized. Listening for live meeting recordings...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("event")
        print(f"\n🔔 [Zoom Webhook] Received live event: '{event_type}'")
        
        event_data = payload.get("payload", {}).get("object", {})
        
        if event_type == "recording.completed":
            meeting_id = event_data.get("id")
            topic = event_data.get("topic", "Live Meeting")
            print(f"🚨 [Live Alert] Cloud Recording & Transcript ready for: '{topic}' (ID: {meeting_id})!")
            
            # In production, yahan se direct recording_files array me se TRANSCRIPT nikal kar
            # event bus me push kiya jata hai taaki AI immediate summary bana sake.
            return {"status": "processed", "meeting_id": meeting_id, "topic": topic}
            
        return {"status": "ignored", "reason": f"Event '{event_type}' not configured."}

zoom_webhook_handler = ZoomWebhookHandler()