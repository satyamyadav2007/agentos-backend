from typing import List
from datetime import datetime
from integrations.ga4.models.event import GA4DropoffModel

class GA4BehaviorExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_funnel_dropoffs(self) -> List[GA4DropoffModel]:
        print(f"📊 [GA4 Extractor] Running Funnel Analysis on Property...")
        
        # A typical GA4 RunReportRequest payload for Custom Funnels
        payload = {
            "dateRanges": [{"startDate": "7daysAgo", "endDate": "today"}],
            "dimensions": [{"name": "eventName"}],
            "metrics": [{"name": "activeUsers"}, {"name": "eventCount"}]
        }
        
        try:
            # Note: Real funnel analysis in GA4 requires RunFunnelReport, 
            # this is a simplified structure mapping to the AI CPO need.
            raw_data = await self.client.post("runReport", payload=payload)
            rows = raw_data.get("rows", [])
            
            anomalies = []
            
            # Mocking the drop-off calculation logic for the AI engine
            for row in rows:
                event_name = row["dimensionValues"][0]["value"]
                users = int(row["metricValues"][0]["value"])
                
                # Simulating an AI analysis detection of a drop-off
                if event_name in ["checkout_step_2", "add_to_cart", "payment_initiate"]:
                    anomalies.append(GA4DropoffModel(
                        event_name=event_name,
                        drop_percentage=42.5, # In production, calculate against previous step
                        active_users_affected=users,
                        date_detected=datetime.utcnow(),
                        funnel_step=event_name
                    ))
                    
            print(f"   ✅ Extracted {len(anomalies)} Behavior Anomalies.")
            return anomalies
            
        except Exception as e:
            print(f"🚨 [GA4 Extractor] Failed to fetch behavior data: {e}")
            return []