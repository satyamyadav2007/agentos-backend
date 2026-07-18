from typing import Dict, Any
from fastapi import BackgroundTasks
from .normalizer import SlackNormalizer
import asyncio

# 🔥 Naya Background Function: Yeh function bina Slack ko wait karaye aaram se chalega
async def process_slack_event_background(event: Dict[str, Any], channel_id: str):
    print("⚙️ [AgentOS Background Task] Handoff to AI Orchestrator started for Live Slack Event...")
    try:
        # Convert to AgentOS Universal format
        normalized_event = SlackNormalizer.normalize_message(event, channel_id)
        
        # Heavy AI processing
        from orchestrator import run_orchestrator
        await run_orchestrator(github_issues=[normalized_event], user_email="satyam@startup.com")
        
        print("✅ [AgentOS Background Task] Live AI Processing Complete!")
    except Exception as e:
        print(f"🚨 [AgentOS Background Task Error]: {e}")


class SlackWebhookHandler:
    def __init__(self):
        print("🕸️ [Slack Webhook] Initialized. Listening for live workspace events...")
        
    # ⚡ FIX: 'background_tasks' parameter add kiya hai
    async def handle_event(self, payload: Dict[str, Any], background_tasks: BackgroundTasks) -> Dict[str, Any]:
        # 1. Slack URL Verification Challenge (Required for initial setup)
        if payload.get("type") == "url_verification":
            print("🔗 [Slack Webhook] Responding to URL verification challenge.")
            return {"challenge": payload.get("challenge")}

        # 2. Process Live Events
        event = payload.get("event", {})
        event_type = event.get("type")
        
        print(f"\n🔔 [Slack Webhook] Received live event: '{event_type}'")
        
        # We only care about new messages for now
        if event_type == "message" and not event.get("subtype"):
            
            # Avoid infinite loops: Ignore messages sent by the bot itself
            if event.get("bot_id"):
                return {"status": "ignored", "reason": "Bot message"}

            channel_id = event.get("channel", "unknown_channel")
            print(f"🚨 [Live Alert] New message in channel {channel_id}. Delegating to background task...")
            
            # 🔥 FIRE AND FORGET: AI processing ko background mein daal do
            background_tasks.add_task(process_slack_event_background, event, channel_id)
            
            # Slack ko turant 200 OK bhej do taaki wo retry na kare
            return {"status": "processing_in_background", "type": "message"}
            
        return {"status": "ignored", "reason": f"Event type '{event_type}' not tracked."}

slack_webhook_handler = SlackWebhookHandler()