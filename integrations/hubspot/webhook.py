from typing import Dict, Any, List

class HubSpotWebhookHandler:
    def __init__(self):
        print("🕸️ [HubSpot Webhook] Initialized. Listening for Growth events...")
        
    async def handle_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        print(f"\n🔔 [HubSpot Webhook] Received {len(events)} live events!")
        
        processed_count = 0
        for event in events:
            event_type = event.get("subscriptionType")
            object_id = event.get("objectId")
            
            # We are most interested in Deal creations for now
            if event_type == "deal.creation":
                print(f"🚨 [Live Alert] New HubSpot Deal Created (ID: {object_id})!")
                
                # NOTE: Webhook only sends ID. You'd typically call the API here to get full deal details 
                # using the HubSpotClient, normalize it, and pass it to Orchestrator.
                
                processed_count += 1
                
        return {"status": "processed", "events_handled": processed_count}

hubspot_webhook_handler = HubSpotWebhookHandler()