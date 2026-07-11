from typing import Dict, Any
from .models.post import CommunityPostModel

class CommunityNormalizer:
    
    @staticmethod
    def normalize_post(post: CommunityPostModel) -> Dict[str, Any]:
        """Converts a Community Post into an AgentOS UniversalEvent."""
        
        # Escalate if the community post is going viral (high views/replies)
        severity = "High" if post.is_trending else "Medium"

        return {
            "source": "community",
            "entity_type": "discussion",
            "repository": "User_Forum",
            "title": f"Forum Topic: {post.title}",
            "description": f"Content Snippet: {post.content[:1000]}",
            "author": post.author_username,
            "severity": severity,
            "timestamp": post.created_at.isoformat(),
            "metadata": {
                "topic_id": post.id,
                "views": post.views,
                "replies": post.reply_count,
                "tags": post.tags
            },
            "linked_entities": []
        }