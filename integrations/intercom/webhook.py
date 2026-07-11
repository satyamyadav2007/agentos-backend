from typing import Dict, Any

class IntercomWebhookHandler:
    def __init__(self):
        print("🕸️ [Intercom Webhook] Initialized. Listening for live customer chats...")
        
    async def handle_event(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", "unknown")
        print(f"\n🔔 [Intercom Webhook] Received event: '{topic}'")
        
        # Intercom puts the actual object inside data.item
        data_item = payload.get("data", {}).get("item", {})
        
        if topic.startswith("conversation."):
            conversation_id = data_item.get("id", "UNKNOWN")
            print(f"🚨 [Live Alert] Intercom Conversation {conversation_id} updated!")
            
            # TODO: Add Normalization and pass to Orchestrator here (similar to Salesforce/Zendesk)
            return {"status": "processed", "type": topic, "conversation_id": conversation_id}
            
        return {"status": "ignored", "reason": f"Event '{topic}' not tracked."}

intercom_webhook_handler = IntercomWebhookHandler()