from typing import Dict, Any
from .normalizer import SalesforceNormalizer
from .models.account import SalesforceAccountModel

class SalesforceWebhookHandler:
    def __init__(self):
        print("🕸️ [Salesforce Webhook] Initialized. Listening for live Revenue events...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Assuming Salesforce Flow sends a JSON with 'object_type' and 'record'
        object_type = payload.get("object_type", "Unknown")
        print(f"\n🔔 [Salesforce Webhook] Received live event for: '{object_type}'")
        
        raw_record = payload.get("record")
        if not raw_record:
            return {"status": "error", "message": "No record data found in payload"}

        record_id = raw_record.get("Id", "UNKNOWN")
        print(f"🚨 [Live Alert] Salesforce {object_type} (ID: {record_id}) was updated!")
        
        try:
            # Currently handling Accounts for Revenue Risk (Module 6)
            if object_type == "Account":
                # 1. Validate incoming JSON with our strict Pydantic Model
                account_model = SalesforceAccountModel(**raw_record)
                
                # 2. Normalize to Universal Format
                normalized_event = SalesforceNormalizer.normalize_account(account_model)
                
                # 3. Hand off to the AI Brain!
                print("⚙️ [AgentOS] Handoff to AI Orchestrator started for Live Salesforce Event...")
                from orchestrator import run_orchestrator
                
                await run_orchestrator(github_issues=[normalized_event], user_email="satyam@startup.com")
                print("✅ [AgentOS] Live AI Processing Complete for Salesforce!")
                
                return {"status": "processed", "type": object_type, "record_id": record_id}
            else:
                return {"status": "ignored", "reason": f"Tracking for {object_type} is not yet enabled."}
            
        except Exception as e:
            print(f"🚨 [Salesforce Webhook Validation Error]: {e}")
            return {"status": "error", "message": str(e)}

salesforce_webhook_handler = SalesforceWebhookHandler()