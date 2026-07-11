from typing import Dict, Any

class GitHubNormalizer:
    """Converts GitHub-specific Pydantic models/dicts into AgentOS UniversalEvents."""
    
    @staticmethod
    def normalize_issue(issue_data: Dict[str, Any], repo_name: str) -> Dict[str, Any]:
        """Normalizes a GitHub Issue."""
        
        title = issue_data.get("title", "")
        labels = [label.get("name", "").lower() for label in issue_data.get("labels", [])]
        
        # Smart AI Pre-processing for Severity based on labels
        severity = "Medium"
        if any(keyword in labels for keyword in ["bug", "critical", "p0", "urgent"]):
            severity = "High"
        elif "enhancement" in labels or "feature" in labels:
            severity = "Low"

        return {
            "source": "github",
            "entity_type": "issue",
            "repository": repo_name,
            "title": title,
            "description": issue_data.get("body", "No description provided."),
            "author": issue_data.get("user", {}).get("login", "Unknown"),
            "severity": severity,
            "timestamp": issue_data.get("created_at"),
            "metadata": {
                "github_id": issue_data.get("id"),
                "number": issue_data.get("number"),
                "state": issue_data.get("state"),
                "labels": labels
            },
            "linked_entities": [] # For GraphDB mapping later
        }

    @staticmethod
    def normalize_pr(pr_data: Dict[str, Any], repo_name: str) -> Dict[str, Any]:
        """Normalizes a GitHub Pull Request."""
        return {
            "source": "github",
            "entity_type": "pull_request",
            "repository": repo_name,
            "title": pr_data.get("title", ""),
            "description": pr_data.get("body", "No description provided."),
            "author": pr_data.get("user", {}).get("login", "Unknown"),
            "severity": "Medium", # PRs usually have Medium risk until analyzed
            "timestamp": pr_data.get("created_at"),
            "metadata": {
                "github_id": pr_data.get("id"),
                "number": pr_data.get("number"),
                "state": pr_data.get("state"),
                "merged": pr_data.get("merged", False),
                "branch": pr_data.get("head", {}).get("ref", "unknown")
            },
            "linked_entities": []
        }