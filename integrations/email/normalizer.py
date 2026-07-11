from typing import Dict, Any
from .models.thread import EmailThreadModel

class EmailNormalizer:
    
    @staticmethod
    def normalize_thread(thread: EmailThreadModel) -> Dict[str, Any]:
        """Converts Email Thread (Gmail/Outlook) into AgentOS UniversalEvent."""
        
        latest = thread.latest_message
        if not latest:
            raise ValueError("Thread has no messages.")
            
        # Module 5: Escalation Intelligence
        severity = "Critical" if thread.is_executive_escalation else "Medium"

        return {
            "source": "email",
            "provider": thread.provider,
            "entity_type": "thread",
            "repository": "Enterprise_Inbox", 
            "title": latest.subject,
            "description": f"Latest msg from {latest.sender}: {latest.body_text}",
            "author": latest.sender,
            "severity": severity,
            "timestamp": latest.timestamp.isoformat(),
            "metadata": {
                "thread_id": thread.id,
                "is_escalated": thread.is_executive_escalation,
                "participants": list(set([latest.sender] + latest.recipients + latest.cc))
            },
            # Will be linked to Salesforce Account and Jira Issues in the Graph!
            "linked_entities": [] 
        }