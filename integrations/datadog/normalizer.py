from typing import Dict, Any
from .models.monitor import DatadogEventModel

class DatadogNormalizer:
    
    @staticmethod
    def normalize_alert(alert: DatadogEventModel) -> Dict[str, Any]:
        """Converts a Datadog APM/Infra Alert into an AgentOS UniversalEvent."""
        
        if alert.is_critical_incident:
            severity = "Critical"
        elif alert.alert_type == "error":
            severity = "High"
        elif alert.alert_type == "warning":
            severity = "Medium"
        else:
            severity = "Low"

        return {
            "source": "datadog",
            "entity_type": "monitor_alert",
            "repository": f"Infra_{alert.source_type_name}", 
            "title": alert.title,
            "description": alert.text[:1500], # Prevent context overflow
            "author": "Datadog_System",
            "severity": severity,
            "timestamp": alert.date_happened.isoformat(),
            "metadata": {
                "alert_id": alert.id,
                "host": alert.host,
                "tags": alert.tags
            },
            # Graph Connections! Module 7: Link GitHub deployment hash to Datadog Incident
            "linked_entities": [] 
        }