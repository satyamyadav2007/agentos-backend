from typing import Dict, Any
from .models.post import RedditPostModel

class RedditNormalizer:
    
    @staticmethod
    def normalize_post(post: RedditPostModel) -> Dict[str, Any]:
        """Converts Reddit Post into AgentOS UniversalEvent."""
        
        # High engagement posts get Critical severity for PM review
        severity = "High" if post.total_engagement > 50 else "Medium"

        return {
            "source": "reddit",
            "entity_type": "post",
            "repository": f"r/{post.subreddit}", # E.g., r/SaaS or r/OpenAI
            "title": post.title,
            "description": post.selftext[:1000], # Cap text for AI efficiency
            "author": f"u/{post.author}",
            "severity": severity,
            "timestamp": post.created_utc.isoformat(),
            "metadata": {
                "reddit_id": post.id,
                "engagement_score": post.total_engagement,
                "url": f"https://reddit.com{post.url}" if post.url.startswith("/") else post.url
            },
            "linked_entities": [] # Ready to connect to Zendesk & Jira!
        }