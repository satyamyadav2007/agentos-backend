from typing import Dict, Any

class DiscordWebhookHandler:
    def __init__(self):
        print("🕸️ [Discord Webhook] Initialized. Listening for live community events...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("type", "unknown")
        print(f"\n🔔 [Discord Webhook] Received live event: '{event_type}'")
        
        if event_type == "message_create":
            message_content = payload.get("content", "")
            author = payload.get("author", "Unknown User")
            
            print(f"🚨 [Live Alert] New Community Feedback from {author}!")
            
            # TODO: Normalize and pass to AI Orchestrator (similar to other apps)
            return {"status": "processed", "type": event_type}
            
        return {"status": "ignored", "reason": f"Event '{event_type}' not tracked."}

discord_webhook_handler = DiscordWebhookHandler()