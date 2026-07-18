from typing import Dict, Any, List
from integrations.slack.normalizer import SlackNormalizer
from integrations.slack.discovery import SlackDiscovery

class SlackSyncService:
    def __init__(self, client):
        self.client = client
        self.discovery = SlackDiscovery(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Slack Sync Service] Starting Enterprise Workspace Sync...")
        
        # 1. Module 2: Workspace Discovery
        channels = await self.discovery.fetch_channels()
        if not channels:
            print("⚠️ [Slack Sync] No channels found.")
            return []
            
        all_normalized_events = []
        
        # Target important channels first to avoid API spam (e.g., #engineering, #alerts, #general)
        target_channels = [c for c in channels if any(k in c['name'].lower() for k in ['eng', 'dev', 'alert', 'support', 'general', 'product'])]
        if not target_channels:
            target_channels = channels[:5] # Fallback to top 5 if naming convention doesn't match
            
        # 2. Module 3, 4, 12: Deep Extraction & Thread Intelligence
        for channel in target_channels:
            chan_id = channel["id"]
            chan_name = channel["name"]
            
            print(f"💬 [Slack Sync] Extracting intelligence from #{chan_name}...")
            
            try:
                # Fetch recent messages
                history_res = await self.client.get("conversations.history", params={"channel": chan_id, "limit": 50})
                messages = history_res.get("messages", [])
                
                for msg in messages:
                    # Ignore bot messages or empty system messages
                    if msg.get("type") == "message" and not msg.get("bot_id"):
                        normalized = SlackNormalizer.normalize_message(msg, chan_name)
                        
                        # 🧵 Module 12: Thread Intelligence
                        # If this message is tagged as an Incident or Decision, AND it has replies, fetch the thread!
                        thread_ts = msg.get("thread_ts")
                        reply_count = int(msg.get("reply_count", 0))
                        
                        if thread_ts and reply_count > 0 and (normalized["entity_type"] == "incident" or normalized["metadata"]["contains_decision"]):
                            thread_res = await self.client.get("conversations.replies", params={"channel": chan_id, "ts": thread_ts, "limit": 20})
                            replies = thread_res.get("messages", [])
                            
                            # Append thread context directly to the description for the AI Brain
                            thread_text = "\n".join([f"- {r.get('text')}" for r in replies[1:] if r.get('type') == 'message'])
                            if thread_text:
                                normalized["description"] += f"\n\n--- Thread Context ---\n{thread_text}"
                                
                        all_normalized_events.append(normalized)
                        
            except Exception as e:
                print(f"🚨 [Slack Sync Error] Failed extracting channel {chan_name}: {e}")
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_normalized_events)} high-value events from Slack!")
        return all_normalized_events