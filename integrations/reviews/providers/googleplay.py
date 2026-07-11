import httpx
from datetime import datetime
from typing import List
from .base import BaseReviewProvider
from ..models.review import AppReviewModel

class GooglePlayProvider(BaseReviewProvider):
    """Google Play Store Reviews Provider."""
    
    def __init__(self, app_id: str, country: str = "us", lang: str = "en"):
        # app_id is the package name here, e.g., com.company.app
        self.app_id = app_id
        self.country = country
        self.lang = lang
        self.timeout = httpx.Timeout(20.0)

    async def fetch_recent_reviews(self, limit: int = 50) -> List[AppReviewModel]:
        print(f"🤖 [Google Play Provider] Fetching latest reviews for Package: {self.app_id}...")
        
        # NOTE: In a production environment, you would use the Google Play Developer API 
        # (Requires Service Account JSON) or a library like `google-play-scraper`.
        # Here we mock the HTTP extraction logic for the architecture.
        
        try:
            # Simulated API/Scraper response
            mock_play_data = [
                {
                    "id": "gp_12345",
                    "title": "Keeps crashing",
                    "text": "After the recent update, the app just shows a blank screen and crashes.",
                    "score": 1,
                    "version": "8.1.0",
                    "date": datetime.utcnow()
                },
                {
                    "id": "gp_12346",
                    "title": "Good but needs dark mode",
                    "text": "Love the app, but a dark mode would be great for night time.",
                    "score": 4,
                    "version": "8.0.5",
                    "date": datetime.utcnow()
                }
            ]
            
            reviews = []
            for entry in mock_play_data[:limit]:
                reviews.append(AppReviewModel(
                    id=entry["id"],
                    provider="googleplay",
                    app_id=self.app_id,
                    title=entry["title"],
                    body=entry["text"],
                    rating=entry["score"],
                    version=entry.get("version", "unknown"),
                    country=self.country,
                    language=self.lang,
                    created_at=entry["date"]
                ))
            
            print(f"   ✅ Extracted {len(reviews)} Google Play reviews.")
            return reviews
                
        except Exception as e:
            print(f"🚨 [Google Play Provider] Failed: {e}")
            return []