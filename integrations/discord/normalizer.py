from typing import Dict, Any
from .models.message import DiscordMessageModel

class DiscordNormalizer:
    
    @staticmethod
    def normalize_message(message: DiscordMessageModel, server_name: str = "Community Server") -> Dict[str, Any]:
        """Converts Discord Message/Forum Post into AgentOS UniversalEvent."""
        
        # High upvotes indicate strong community demand or severe bug
        severity = "High" if message.upvote_count > 20 else "Medium"

        return {
            "source": "discord",
            "entity_type": "forum_post", # or "message"
            "repository": server_name, 
            "title": f"Community Feedback by {message.author.username}",
            "description": message.content,
            "author": message.author.username,
            "severity": severity,
            "timestamp": message.timestamp.isoformat(),
            "metadata": {
                "discord_message_id": message.id,
                "channel_id": message.channel_id,
                "upvotes": message.upvote_count,
                "has_attachments": len(message.attachments) > 0
            },
            "linked_entities": [] # Ready to connect to GitHub & Jira in Neo4j
        }