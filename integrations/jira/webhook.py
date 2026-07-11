from typing import Dict, Any
from .normalizer import JiraNormalizer

class JiraWebhookHandler:
    def __init__(self):
        print("🕸️ [Jira Webhook] Initialized. Listening for live project events...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Jira bhejta hai 'webhookEvent' jisme event ka type hota hai
        event_type = payload.get("webhookEvent")
        
        print(f"\n🔔 [Jira Webhook] Received live event: '{event_type}'")
        
        # Hum sirf issue creation aur updates ko track kar rahe hain abhi
        if event_type in ["jira:issue_created", "jira:issue_updated"]:
            raw_issue = payload.get("issue")
            
            if not raw_issue:
                return {"status": "error", "message": "No issue data in payload"}

            issue_key = raw_issue.get("key", "UNKNOWN")
            print(f"🚨 [Live Alert] Jira Issue {issue_key} was {event_type.split('_')[-1]}!")
            
            # Convert to AgentOS Universal format using the normalizer we already built
            normalized_event = JiraNormalizer.normalize_issue(raw_issue)
            
            # Hand off to the AI Brain!
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Live Jira Event...")
            from orchestrator import run_orchestrator
            
            # Using the identical orchestrator pipeline
            await run_orchestrator(github_issues=[normalized_event], user_email="satyam@startup.com")
            print("✅ [AgentOS] Live AI Processing Complete for Jira!")
            
            return {"status": "processed", "type": event_type, "data": normalized_event}
            
        return {"status": "ignored", "reason": f"Event type '{event_type}' not tracked."}

jira_webhook_handler = JiraWebhookHandler()