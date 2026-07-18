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
            "id": str(issue_data.get("id", issue_data.get("number", "unknown"))),
            "source": "github",
            "entity_type": "issue",
            "repository": repo_name,
            "title": title,
            "description": issue_data.get("body", "No description provided."),
            "author": issue_data.get("user", {}).get("login", "Unknown"),
            "severity": severity,
            "timestamp": issue_data.get("created_at"),
            "engagement_score": 0.0,  # ⚡ FIXED: Added for Event Bus compatibility
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
            # ⚡ FIXED: Changed issue_data to pr_data
            "id": str(pr_data.get("id", pr_data.get("number", "unknown"))),
            "source": "github",
            "entity_type": "pull_request",
            "repository": repo_name,
            "title": pr_data.get("title", ""),
            "description": pr_data.get("body", "No description provided."),
            "author": pr_data.get("user", {}).get("login", "Unknown"),
            "severity": "Medium", # PRs usually have Medium risk until analyzed
            "timestamp": pr_data.get("created_at"),
            "engagement_score": 0.0,  # ⚡ FIXED: Added for Event Bus compatibility
            "metadata": {
                "github_id": pr_data.get("id"),
                "number": pr_data.get("number"),
                "state": pr_data.get("state"),
                "merged": pr_data.get("merged", False),
                "branch": pr_data.get("head", {}).get("ref", "unknown"),
                "created_at": pr_data.get("created_at"), 
                "merged_at": pr_data.get("merged_at")
            },
            "linked_entities": []
        }

    @staticmethod
    def normalize_commit(commit_model_dict: Dict[str, Any], repo_name: str) -> Dict[str, Any]:
        """Normalizes a GitHub Commit into a Universal Event."""
        commit_info = commit_model_dict.get("commit", {})
        message = commit_info.get("message", "No message")
        author_name = commit_info.get("author", {}).get("name", "Unknown")
        
        # Simple AI heuristic for commit severity
        severity = "Medium"
        if any(keyword in message.lower() for keyword in ["fix", "hotfix", "critical", "revert"]):
            severity = "High"

        return {
            # ⚡ FIXED: Commits use 'sha', not id/number. Changed raw_issue to commit_model_dict
            "id": str(commit_model_dict.get("sha", "unknown")),
            "source": "github",
            "entity_type": "commit",
            "repository": repo_name,
            "title": message.split("\n")[0][:100], # First line as title
            "description": message,
            "severity": severity,
            "author": author_name,
            "engagement_score": 0.0,  # ⚡ FIXED: Added for Event Bus compatibility
            "metadata_json": {
                "sha": commit_model_dict.get("sha"),
                "url": commit_model_dict.get("html_url")
            }
        }

    @staticmethod
    def normalize_action(action_dict: Dict[str, Any], repo_name: str) -> Dict[str, Any]:
        """Normalizes a GitHub Action Workflow Run."""
        conclusion = action_dict.get("conclusion")
        
        severity = "Low"
        if conclusion in ["failure", "timed_out", "cancelled"]:
            severity = "High" # Failed builds are critical blockers
            
        return {
            # ⚡ FIXED: Changed raw_run to action_dict
            "id": str(action_dict.get("id", "unknown")),
            "source": "github",
            "entity_type": "ci_cd_run",
            "repository": repo_name,
            "title": f"Workflow: {action_dict.get('name')} ({conclusion})",
            "description": f"Triggered by {action_dict.get('event')} on branch {action_dict.get('head_branch')}",
            "severity": severity,
            "author": action_dict.get("actor", {}).get("login", "System"),
            "engagement_score": 0.0,  # ⚡ FIXED: Added for Event Bus compatibility
            "metadata_json": {
                "run_id": action_dict.get("id"),
                "html_url": action_dict.get("html_url"),
                "status": action_dict.get("status")
            }
        } 

    @staticmethod
    def normalize_release(release_dict: Dict[str, Any], repo_name: str) -> Dict[str, Any]:
        """Normalizes a GitHub Release into a Universal Event."""
        is_draft = release_dict.get("draft", False)
        is_prerelease = release_dict.get("prerelease", False)
        
        # Production releases are inherently 'Medium' risk events because they change the live environment
        severity = "Low"
        if not is_draft and not is_prerelease:
            severity = "Medium" 

        title_name = release_dict.get('name')
        if not title_name:
            title_name = release_dict.get('tag_name', 'Unknown Version')

        return {
            # ⚡ FIXED: Changed raw_release to release_dict
            "id": str(release_dict.get("id", "unknown")),
            "source": "github",
            "entity_type": "release",
            "repository": repo_name,
            "title": f"Release: {title_name}",
            "description": release_dict.get("body", "No release notes provided.")[:1000] if release_dict.get("body") else "No release notes provided.",
            "severity": severity,
            "author": release_dict.get("author", {}).get("login", "System"),
            "engagement_score": 0.0,  # ⚡ FIXED: Added for Event Bus compatibility
            "metadata_json": {
                "tag_name": release_dict.get("tag_name"),
                "is_production": not is_draft and not is_prerelease,
                "url": release_dict.get("html_url")
            }
        } 

    @staticmethod
    def normalize_discussion(discussion_dict: Dict[str, Any], repo_name: str) -> Dict[str, Any]:
        """Normalizes a GitHub GraphQL Discussion into a Universal Event."""
        
        category = discussion_dict.get("category", {}).get("name", "General")
        
        # Smart AI Pre-processing: Bugs or Feature Requests have higher impact than Q&A
        severity = "Low"
        if category.lower() in ["bug", "ideas", "feature request"]:
            severity = "Medium"
            
        author_data = discussion_dict.get("author")
        author_name = author_data.get("login") if author_data else "Unknown"
        
        # ⚡ FIXED: Changed raw_discussion to discussion_dict
        discussion_id = discussion_dict.get("id") or discussion_dict.get("number", "unknown")

        return {
            "id": str(discussion_id),
            "source": "github",
            "entity_type": "discussion",
            "repository": repo_name,
            "title": f"[{category}] {discussion_dict.get('title', 'Untitled')}",
            "description": discussion_dict.get("bodyText", "No content provided.")[:1000] if discussion_dict.get("bodyText") else "No content provided.",
            "severity": severity,
            "author": author_name,
            "engagement_score": 0.0,  # ⚡ FIXED: Added for Event Bus compatibility
            "metadata_json": {
                "github_id": discussion_dict.get("id"),
                "category": category,
                "url": discussion_dict.get("url"),
                "created_at": discussion_dict.get("createdAt")
            }
        }