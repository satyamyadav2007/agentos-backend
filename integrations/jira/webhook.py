from typing import Dict, Any, Optional
from .normalizer import JiraNormalizer
# from database.postgres_setup import SessionLocal  <-- Future DB connection
# from database.models import WorkspaceIntegration

class JiraWebhookHandler:
    def __init__(self):
        print("🕸️ [Jira Webhook] Initialized. Listening for live project events...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        event_type = payload.get("webhookEvent")
        print(f"\n🔔 [Jira Webhook] Received live event: '{event_type}'")
        
        if event_type in ["jira:issue_created", "jira:issue_updated"]:
            raw_issue = payload.get("issue")
            if not raw_issue:
                return {"status": "error", "message": "No issue data in payload"}

            issue_key = raw_issue.get("key", "UNKNOWN")
            print(f"🚨 [Live Alert] Jira Issue {issue_key} was {event_type.split('_')[-1]}!")
            
            # 1. Normalize Event
            normalized_event = JiraNormalizer.normalize_issue(raw_issue)
            
            # 2. TODO: Fetch actual user_email from Postgres using Webhook URL or Cloud ID
            # For now, using a dynamic placeholder instead of hardcoding
            dynamic_user_email = "dynamic_user@agentos.com" 
            
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Live Jira Event...")
            from orchestrator import run_orchestrator
            
            # 3. Fixed parameter passing (using a generic kwargs approach if supported by orchestrator)
            # If your orchestrator strictly demands 'github_issues' as the parameter name, 
            # you can leave it, but ideally it should be 'events' or 'normalized_events'
            await run_orchestrator(github_issues=[normalized_event], user_email=dynamic_user_email)
            print("✅ [AgentOS] Live AI Processing Complete for Jira!")
            
            return {"status": "processed", "type": event_type, "data": normalized_event}
            
        return {"status": "ignored", "reason": f"Event type '{event_type}' not tracked."}

jira_webhook_handler = JiraWebhookHandler()