from typing import Dict, Any, List
from integrations.analytics.normalizer import AnalyticsNormalizer
from integrations.analytics.providers.base import BaseAnalyticsProvider

class AnalyticsSyncService:
    """Orchestrates extraction and normalization across ALL analytics tools."""
    
    def __init__(self, provider: BaseAnalyticsProvider):
        # Polymorphism in action: The service doesn't care if this is PostHog or Mixpanel
        self.provider = provider
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Analytics Sync] Starting Intelligence Sync using provider...")
        
        all_universal_events = []
        
        # 1. Fetch Events using whatever provider was passed in
        events_models = await self.provider.fetch_recent_events()
        
        # 2. Normalize to Universal Format
        for event in events_models:
            # We filter for high-value events to keep the AI signal-to-noise ratio high
            if event.event_name not in ["$pageview", "$screen"]: 
                normalized = AnalyticsNormalizer.normalize_event(event)
                all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} behavioral signals!")
        return all_universal_events