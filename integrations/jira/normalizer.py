from typing import Dict, Any

class JiraNormalizer:
    
    @staticmethod
    def normalize_issue(raw_issue: Dict[str, Any]) -> Dict[str, Any]:
        """Converts a raw Jira Issue into the AgentOS UniversalEvent format."""
        fields = raw_issue.get("fields", {})
        issue_type = fields.get("issuetype", {}).get("name", "Task").lower()
        
        jira_priority = fields.get("priority", {}).get("name", "Medium").lower()
        severity_map = {"highest": "Critical", "high": "High", "medium": "Medium", "low": "Low", "lowest": "Low"}
        severity = severity_map.get(jira_priority, "Medium")
        
        description_raw = fields.get("description")
        description_text = str(description_raw) if isinstance(description_raw, dict) else (description_raw or "No description provided.")

        assignee = fields.get("assignee")
        author = assignee.get("displayName") if assignee else "Unassigned"

        return {
            "id": str(raw_issue.get("id", raw_issue.get("key"))),
            "source": "jira",
            "entity_type": issue_type, 
            "repository": raw_issue.get("key", "").split("-")[0],
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

    @staticmethod
    def normalize_epic(raw_epic: Dict[str, Any], project_key: str) -> Dict[str, Any]:
        """Converts a Jira Epic into the AgentOS UniversalEvent format."""
        fields = raw_epic.get("fields", {})
        return {
            "id": str(raw_epic.get("id", raw_epic.get("key"))),
            "source": "jira",
            "entity_type": "epic",
            "repository": project_key,
            "title": fields.get("summary", "Untitled Epic"),
            "description": "Epic level initiative.",
            "author": fields.get("creator", {}).get("displayName", "System"),
            "severity": "High", # Epics usually have high business impact
            "timestamp": fields.get("created"),
            "metadata": {
                "jira_id": raw_epic.get("id"),
                "key": raw_epic.get("key"),
                "status": fields.get("status", {}).get("name")
            },
            "linked_entities": []
        }

    @staticmethod
    def normalize_sprint(raw_sprint: Dict[str, Any], project_key: str) -> Dict[str, Any]:
        """Converts an Active Sprint into the AgentOS UniversalEvent format."""
        return {
            "id": str(raw_sprint.get("id")),
            "source": "jira",
            "entity_type": "sprint",
            "repository": project_key,
            "title": raw_sprint.get("name", "Unnamed Sprint"),
            "description": raw_sprint.get("goal", "No sprint goal defined."),
            "author": "Jira Agile Board",
            "severity": "Medium",
            "timestamp": raw_sprint.get("startDate"),
            "metadata": {
                "jira_id": str(raw_sprint.get("id")),
                "status": raw_sprint.get("state", "active"),
                "end_date": raw_sprint.get("endDate")
            },
            "linked_entities": []
        }