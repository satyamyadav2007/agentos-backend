import httpx
from datetime import datetime
from typing import List
from .base import BaseReviewProvider
from ..models.review import AppReviewModel

class ChromeWebStoreProvider(BaseReviewProvider):
    """Chrome Web Store Reviews Provider."""
    
    def __init__(self, app_id: str):
        # app_id is the 32-character extension ID
        self.app_id = app_id
        self.timeout = httpx.Timeout(20.0)

    async def fetch_recent_reviews(self, limit: int = 50) -> List[AppReviewModel]:
        print(f"🌐 [Chrome Store Provider] Fetching latest reviews for Extension ID: {self.app_id}...")
        
        # NOTE: Chrome Web Store API requires OAuth for developers to read reviews.
        # This is the architectural representation of that data fetch.
        
        try:
            # Simulated API response from Chrome Web Store Developer API
            mock_chrome_data = [
                {
                    "id": "cw_9876",
                    "title": "CPU Usage is too high",
                    "text": "Since yesterday, this extension is taking up 50% of my CPU.",
                    "score": 2,
                    "version": "2.4.1",
                    "date": datetime.utcnow()
                }
            ]
            
            reviews = []
            for entry in mock_chrome_data[:limit]:
                reviews.append(AppReviewModel(
                    id=entry["id"],
                    provider="chrome",
                    app_id=self.app_id,
                    title=entry["title"],
                    body=entry["text"],
                    rating=entry["score"],
                    version=entry.get("version", "unknown"),
                    country="global", # Chrome reviews are often global
                    language="en",
                    created_at=entry["date"]
                ))
            
            print(f"   ✅ Extracted {len(reviews)} Chrome Web Store reviews.")
            return reviews
                
        except Exception as e:
            print(f"🚨 [Chrome Store Provider] Failed: {e}")
            return []