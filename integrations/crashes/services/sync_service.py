from typing import Dict, Any, List
from integrations.crashes.normalizer import CrashNormalizer
from integrations.crashes.providers.base import BaseCrashProvider

class CrashSyncService:
    """Orchestrates extraction and normalization across ALL crash reporting tools."""
    
    def __init__(self, provider: BaseCrashProvider):
        self.provider = provider
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print(f"\n🚀 [Crash Sync] Starting Root Cause & Incident Sync...")
        
        all_universal_events = []
        
        # 1. Fetch Active Crashes
        crash_models = await self.provider.fetch_unresolved_crashes()
        
        # 2. Normalize to Universal Format
        for crash in crash_models:
            normalized = CrashNormalizer.normalize_crash(crash)
            all_universal_events.append(normalized)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} system crashes for Root Cause Analysis!")
        return all_universal_events