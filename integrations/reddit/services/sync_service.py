from typing import Dict, Any, List
from integrations.reddit.extractors.search import RedditSearchExtractor
from integrations.reddit.normalizer import RedditNormalizer

class RedditSyncService:
    """Orchestrates extraction and normalization for Market Intelligence."""
    
    def __init__(self, client):
        self.client = client
        self.search_extractor = RedditSearchExtractor(client)
        
    async def run_full_sync(self, tracking_keywords: List[str]) -> List[Dict[str, Any]]:
        print("\n🚀 [Reddit Sync] Starting Unfiltered Market Intelligence Sync...")
        
        all_universal_events = []
        
        for keyword in tracking_keywords:
            # 1. Fetch Mentions per keyword (Product or Competitor)
            post_models = await self.search_extractor.fetch_product_mentions(keyword)
            
            # 2. Normalize to Universal Format
            for post in post_models:
                # Filter out pure image/link posts without text context if needed
                if post.title or post.selftext:
                    normalized = RedditNormalizer.normalize_post(post)
                    all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} brutal market insights from Reddit!")
        return all_universal_events