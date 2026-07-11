from typing import Dict, Any
from .models.tweet import TweetModel

class TwitterNormalizer:
    
    @staticmethod
    def normalize_tweet(tweet: TweetModel, brand_keyword: str) -> Dict[str, Any]:
        """Converts a Tweet into an AgentOS UniversalEvent."""
        
        # Module 7: Crisis Intelligence escalation
        severity = "Critical" if tweet.is_viral_or_urgent else "Medium"

        return {
            "source": "twitter",
            "entity_type": "tweet",
            "repository": f"BrandTracker_{brand_keyword}", 
            "title": f"Mention by @{tweet.author.username} ({tweet.author.follower_count} followers)",
            "description": tweet.text,
            "author": f"@{tweet.author.username}",
            "severity": severity,
            "timestamp": tweet.created_at.isoformat(),
            "metadata": {
                "tweet_id": tweet.id,
                "retweets": tweet.retweet_count,
                "likes": tweet.like_count,
                "is_viral_or_urgent": tweet.is_viral_or_urgent
            },
            "linked_entities": [] 
        }