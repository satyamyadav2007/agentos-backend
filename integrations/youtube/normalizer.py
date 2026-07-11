from typing import Dict, Any
from .models.comment import YouTubeCommentModel

class YouTubeNormalizer:
    
    @staticmethod
    def normalize_comment(comment: YouTubeCommentModel) -> Dict[str, Any]:
        """Converts YouTube Comment into AgentOS UniversalEvent."""
        
        # High engagement implies many users face the same issue
        severity = "High" if comment.engagement_score > 20 else "Medium"

        return {
            "source": "youtube",
            "entity_type": "comment",
            "repository": f"Video_{comment.video_id}", 
            "title": f"YouTube Feedback by {comment.author_name}",
            "description": comment.text_original,
            "author": comment.author_name,
            "severity": severity,
            "timestamp": comment.published_at.isoformat(),
            "metadata": {
                "youtube_comment_id": comment.id,
                "engagement_score": comment.engagement_score,
                "likes": comment.like_count
            },
            # Neo4j will map this to Zendesk tickets & GitHub Issues (Module 20)
            "linked_entities": [] 
        }