from typing import List
from datetime import datetime
from integrations.twitter.models.tweet import TweetModel, TwitterUserModel

class TweetExtractor:
    def __init__(self, client):
        self.client = client

    async def fetch_brand_mentions(self, query: str, limit: int = 50) -> List[TweetModel]:
        print(f"🐦 [Twitter Extractor] Fetching real-time mentions for query: '{query}'...")
        
        params = {
            "query": query,
            "max_results": limit,
            "tweet.fields": "created_at,public_metrics",
            "expansions": "author_id",
            "user.fields": "public_metrics"
        }
        
        try:
            raw_data = await self.client.get("tweets/search/recent", params=params)
            tweets_data = raw_data.get("data", [])
            users_data = {u["id"]: u for u in raw_data.get("includes", {}).get("users", [])}
            
            standardized_tweets = []
            for t in tweets_data:
                author_info = users_data.get(t.get("author_id"), {})
                metrics = t.get("public_metrics", {})
                author_metrics = author_info.get("public_metrics", {})
                
                author = TwitterUserModel(
                    id=author_info.get("id", "unknown"),
                    username=author_info.get("username", "anonymous"),
                    follower_count=author_metrics.get("followers_count", 0)
                )
                
                standardized_tweets.append(TweetModel(
                    id=t["id"],
                    text=t["text"],
                    author=author,
                    created_at=datetime.fromisoformat(t.get("created_at", "").replace('Z', '+00:00')),
                    retweet_count=metrics.get("retweet_count", 0),
                    like_count=metrics.get("like_count", 0),
                    reply_count=metrics.get("reply_count", 0)
                ))
                
            print(f"   ✅ Extracted {len(standardized_tweets)} Tweets.")
            return standardized_tweets
            
        except Exception as e:
            print(f"🚨 [Twitter Extractor] Failed to fetch tweets: {e}")
            return []