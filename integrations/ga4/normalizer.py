from typing import Dict, Any
from .models.event import GA4DropoffModel

class GA4Normalizer:
    
    @staticmethod
    def normalize_anomaly(anomaly: GA4DropoffModel) -> Dict[str, Any]:
        """Converts a GA4 Behavior Anomaly into an AgentOS UniversalEvent."""
        
        severity = "Critical" if anomaly.is_critical_drop else "Medium"

        return {
            "source": "ga4",
            "entity_type": "event",
            "repository": "Product_Behavior",
            "title": f"High Drop-off Alert: {anomaly.event_name}",
            "description": f"AI detected a {anomaly.drop_percentage}% drop-off at funnel step '{anomaly.event_name}'. Affected active users: {anomaly.active_users_affected}.",
            "author": "GA4_System",
            "severity": severity,
            "timestamp": anomaly.date_detected.isoformat(),
            "metadata": {
                "drop_percentage": anomaly.drop_percentage,
                "users_affected": anomaly.active_users_affected,
                "funnel_step": anomaly.funnel_step
            },
            "linked_entities": []
        }