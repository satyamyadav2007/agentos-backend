import time
import asyncio
from typing import Dict

class RateLimitHandler:
    """Handles GitHub API rate limiting gracefully."""
    
    @staticmethod
    async def check_and_wait(headers: Dict[str, str], buffer: int = 50):
        """
        Checks rate limit headers and pauses execution if limits are dangerously low.
        """
        remaining = int(headers.get("x-ratelimit-remaining", 5000))
        reset_time = int(headers.get("x-ratelimit-reset", time.time()))
        
        if remaining <= buffer:
            sleep_duration = max(reset_time - int(time.time()), 0) + 1
            print(f"⚠️ [Rate Limit] GitHub API limit reaching soon. Only {remaining} left.")
            print(f"⏳ Sleeping for {sleep_duration} seconds until reset...")
            await asyncio.sleep(sleep_duration)
            print("🚀 [Rate Limit] Resuming operations!")
        else:
            # Uncomment below for aggressive logging during debugging
            # print(f"ℹ️ [Rate Limit] {remaining} requests remaining.")
            pass