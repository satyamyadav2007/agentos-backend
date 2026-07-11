from typing import Dict, Any

class JiraNormalizer:
    
    @staticmethod
    def normalize_issue(raw_issue: Dict[str, Any]) -> Dict[str, Any]:
        """Converts a raw Jira Issue into the AgentOS UniversalEvent format."""
        
        fields = raw_issue.get("fields", {})
        issue_type = fields.get("issuetype", {}).get("name", "Task").lower()
        
        # Map Jira priority to AgentOS Severity
        jira_priority = fields.get("priority", {}).get("name", "Medium").lower()
        severity_map = {
            "highest": "Critical",
            "high": "High",
            "medium": "Medium",
            "low": "Low",
            "lowest": "Low"
        }
        severity = severity_map.get(jira_priority, "Medium")
        
        # Extract description (Jira v3 uses Atlassian Document Format, simplifying for now)
        description_raw = fields.get("description")
        description_text = "No description provided."
        if isinstance(description_raw, dict):
            # Extract plain text from ADF if needed, or stringify
            description_text = str(description_raw)
        elif isinstance(description_raw, str):
            description_text = description_raw

        assignee = fields.get("assignee")
        author = assignee.get("displayName") if assignee else "Unassigned"

        return {
            "source": "jira",
            "entity_type": issue_type,  # e.g., 'story', 'bug', 'epic'
            "repository": raw_issue.get("key").split("-")[0], # Project Key as repo equivalent
            "title": fields.get("summary", "Untitled Issue"),
            "description": description_text,
            "author": author,
            "severity": severity,
            "timestamp": fields.get("created"),
            "metadata": {
                "jira_id": raw_issue.get("id"),
                "key": raw_issue.get("key"),
                "status": fields.get("status", {}).get("name")
            },
            "linked_entities": []
        }