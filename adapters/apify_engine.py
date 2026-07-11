import os
import httpx
import traceback
from typing import List, Dict, Any

class ApifyEngine:
    """
    AgentOS Social & Reviews Aggregator
    Fetches real-time unstructured data from Reddit, Twitter, App Store via Apify.
    """
    def __init__(self):
        # 1. Load Real Credentials
        self.api_token = os.environ.get("APIFY_API_TOKEN")
        self.base_url = "https://api.apify.com/v2"
        
        # 2. Map Platforms to your specific Apify Task IDs
        # (You create these tasks in the Apify Console)
        self.tasks = {
            "Reddit": os.environ.get("APIFY_REDDIT_TASK_ID", "default_reddit"),
            "Twitter/X": os.environ.get("APIFY_TWITTER_TASK_ID", "default_twitter"),
            "App Store": os.environ.get("APIFY_APPSTORE_TASK_ID", "default_appstore"),
            "Google Play": os.environ.get("APIFY_GOOGLE_PLAY_TASK_ID", "default_gplay"),
        }
        
        # Keep a healthy timeout for dataset downloads
        self.timeout = httpx.Timeout(30.0)

    # =========================================================================
    # THE REAL DATA INGESTION ENGINE
    # =========================================================================
    
    async def fetch_social_signals(self, platform: str, limit: int = 20) -> List[Dict[str, Any]]:
        print(f"🌍 [Apify Engine] Fetching LIVE signals for {platform}...")
        
        if not self.api_token:
            print("⚠️ [Apify Engine] APIFY_API_TOKEN missing in .env! Returning empty data.")
            return []

        task_id = self.tasks.get(platform)
        if not task_id or task_id.startswith("default_"):
            print(f"⚠️ [Apify Engine] No valid Apify Task ID configured for {platform}.")
            return []

        try:
            # ⚡ PRO-TIP: We fetch the dataset of the LAST COMPLETED RUN.
            # This ensures zero loading time. The dashboard gets instant data.
            url = f"{self.base_url}/actor-tasks/{task_id}/runs/last/dataset/items"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    url,
                    params={
                        "token": self.api_token,
                        "limit": limit
                    }
                )
                
                if response.status_code == 200:
                    raw_data = response.json()
                    print(f"✅ [Apify Engine] Successfully downloaded {len(raw_data)} records from {platform}")
                    
                    # 3. Normalize the messy data into a clean AgentOS format
                    normalized_signals = []
                    for item in raw_data:
                        # Different Apify actors use different keys for text. We catch them all.
                        text_content = item.get("text") or item.get("fullText") or item.get("review") or item.get("title")
                        
                        if text_content:
                            normalized_signals.append({
                                "source_name": platform,
                                "raw_data": text_content,
                                "url": item.get("url", ""),
                                "metadata": item
                            })
                        
                    return normalized_signals
                else:
                    print(f"🚨 [Apify Engine] Apify API Rejected Request: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            print(f"🚨 [Apify Engine] Exception during Apify Network Call: {e}")
            traceback.print_exc()
            return []

# Initialize a singleton instance to be used by main.py routes
apify_connector = ApifyEngine()