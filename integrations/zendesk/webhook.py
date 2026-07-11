from typing import Dict, Any
from .normalizer import ZendeskNormalizer
from .models.ticket import ZendeskTicketModel

class ZendeskWebhookHandler:
    def __init__(self):
        print("🕸️ [Zendesk Webhook] Initialized. Listening for live customer pain points...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Zendesk se hum ek custom JSON expect karenge jisme 'ticket' object hoga
        event_type = payload.get("event_type", "ticket_event")
        print(f"\n🔔 [Zendesk Webhook] Received live event: '{event_type}'")
        
        raw_ticket = payload.get("ticket")
        if not raw_ticket:
            return {"status": "error", "message": "No ticket data found in payload"}

        ticket_id = raw_ticket.get("id", "UNKNOWN")
        print(f"🚨 [Live Alert] Zendesk Ticket #{ticket_id} was created/updated!")
        
        try:
            # 1. Validate incoming JSON with our strict Pydantic Model
            ticket_model = ZendeskTicketModel(**raw_ticket)
            
            # 2. Normalize to Universal Format
            normalized_event = ZendeskNormalizer.normalize_ticket(ticket_model, org_name="Live Customer")
            
            # 3. Hand off to the AI Brain!
            print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Live Zendesk Event...")
            from orchestrator import run_orchestrator
            
            await run_orchestrator(github_issues=[normalized_event], user_email="satyam@startup.com")
            print("✅ [AgentOS] Live AI Processing Complete for Zendesk!")
            
            return {"status": "processed", "type": event_type, "ticket_id": ticket_id}
            
        except Exception as e:
            print(f"🚨 [Zendesk Webhook Validation Error]: {e}")
            return {"status": "error", "message": str(e)}

zendesk_webhook_handler = ZendeskWebhookHandler()