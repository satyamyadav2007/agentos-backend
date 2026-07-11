from typing import Dict, Any
from .normalizer import SlackNormalizer

class SlackWebhookHandler:
    def __init__(self):
        print("🕸️ [Slack Webhook] Initialized. Listening for live workspace events...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Slack URL Verification Challenge (Required for initial setup)
        if payload.get("type") == "url_verification":
            print("🔗 [Slack Webhook] Responding to URL verification challenge.")
            return {"challenge": payload.get("challenge")}

        # 2. Process Live Events
        event = payload.get("event", {})
        event_type = event.get("type")
        
        print(f"\n🔔 [Slack Webhook] Received live event: '{event_type}'")
        
        # We only care about new messages for now (ignore edits/deletes for simplicity)
        if event_type == "message" and not event.get("subtype"):
            
            # Avoid infinite loops: Ignore messages sent by the bot itself
            if event.get("bot_id"):
                return {"status": "ignored", "reason": "Bot message"}

            channel_id = event.get("channel", "unknown_channel")
            print(f"🚨 [Live Alert] New message in channel {channel_id}")
            
            # Convert to AgentOS Universal format
            normalized_event = SlackNormalizer.normalize_message(event, channel_id)
            
            # Hand off to the AI Brain!
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Live Slack Event...")
            from orchestrator import run_orchestrator
            
            # Background task setup might be needed in production so Slack doesn't timeout (requires 200 OK within 3s)
            # For MVP, we await it directly
            await run_orchestrator(github_issues=[normalized_event], user_email="satyam@startup.com")
            print("✅ [AgentOS] Live AI Processing Complete!")
            
            return {"status": "processed", "type": "message", "data": normalized_event}
            
        return {"status": "ignored", "reason": f"Event type '{event_type}' not tracked."}

slack_webhook_handler = SlackWebhookHandler()