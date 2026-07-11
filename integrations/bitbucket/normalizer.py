from typing import Dict, Any
from .models.pr import BitbucketPRModel

class BitbucketNormalizer:
    
    @staticmethod
    def normalize_pr(pr: BitbucketPRModel) -> Dict[str, Any]:
        """Converts a Bitbucket Pull Request into an AgentOS UniversalEvent."""
        
        # Escalate high-risk PRs for AI attention
        severity = "High" if pr.is_risky else "Medium"

        return {
            "source": "bitbucket",
            "entity_type": "pull_request",
            "repository": pr.repository.full_name,
            "title": f"PR #{pr.id}: {pr.title}",
            "description": f"Status: {pr.state} | Author: {pr.author.display_name}\n\n{pr.description[:1000]}",
            "author": pr.author.display_name,
            "severity": severity,
            "timestamp": pr.updated_on.isoformat(),
            "metadata": {
                "pr_id": pr.id,
                "state": pr.state,
                "url": pr.web_url,
                "merge_commit_hash": pr.merge_commit.get("hash") if pr.merge_commit else None
            },
            # Crucial for Module 8 (Executive Chat): Map PRs to Jira Issues via Jira keys in PR titles
            "linked_entities": [] 
        }