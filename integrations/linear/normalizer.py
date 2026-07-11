from typing import Dict, Any
from .models.issue import LinearIssueModel

class LinearNormalizer:
    
    @staticmethod
    def normalize_issue(issue: LinearIssueModel) -> Dict[str, Any]:
        """Converts a Linear Issue into an AgentOS UniversalEvent."""
        
        # If an issue is blocked or urgent, escalate it
        if issue.is_blocked:
            severity = "Critical"
        else:
            severity = issue.severity_label

        return {
            "source": "linear",
            "entity_type": "issue",
            "repository": f"Team_{issue.team.key}", 
            "title": f"[{issue.team.key}] {issue.title}",
            "description": f"State: {issue.state.name} | Assignee: {issue.assignee_name}\n\n{issue.description[:1000]}",
            "author": issue.assignee_name,
            "severity": severity,
            "timestamp": issue.updated_at.isoformat(),
            "metadata": {
                "linear_id": issue.id,
                "status_type": issue.state.type,
                "priority_level": issue.priority,
                "url": issue.url
            },
            # Graph Connections! Module 6: Zendesk -> Linear -> GitHub
            "linked_entities": [] 
        }