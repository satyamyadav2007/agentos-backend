import httpx
from datetime import datetime
from typing import List, Dict, Any
from .base import BaseReviewProvider # Assumed abstract base class
from ..models.review import AppReviewModel

class AppStoreProvider(BaseReviewProvider):
    """Apple App Store Reviews Provider."""
    
    def __init__(self, app_id: str, country: str = "us"):
        self.app_id = app_id
        self.country = country
        self.base_url = f"https://itunes.apple.com/{self.country}/rss/customerreviews"
        self.timeout = httpx.Timeout(20.0)

    async def fetch_recent_reviews(self, limit: int = 50) -> List[AppReviewModel]:
        print(f"🍏 [App Store Provider] Fetching latest reviews for App ID: {self.app_id}...")
        
        url = f"{self.base_url}/id={self.app_id}/sortBy=mostRecent/json"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
                
                # App Store RSS format is slightly quirky
                entries = data.get("feed", {}).get("entry", [])
                
                reviews = []
                for entry in entries:
                    # Skip the first entry if it's the app metadata itself
                    if "author" not in entry: continue
                    
                    reviews.append(AppReviewModel(
                        id=entry.get("id", {}).get("label", "unknown"),
                        provider="appstore",
                        app_id=self.app_id,
                        title=entry.get("title", {}).get("label", "No Title"),
                        body=entry.get("content", {}).get("label", ""),
                        rating=int(entry.get("im:rating", {}).get("label", 0)),
                        version=entry.get("im:version", {}).get("label", "unknown"),
                        country=self.country,
                        created_at=datetime.utcnow() # Apple RSS doesn't always provide precise timestamps easily
                    ))
                
                print(f"   ✅ Extracted {len(reviews)} App Store reviews.")
                return reviews[:limit]
                
        except Exception as e:
            print(f"🚨 [App Store Provider] Failed: {e}")
            return []