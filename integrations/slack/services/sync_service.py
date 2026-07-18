from typing import Dict, Any, List
from integrations.slack.normalizer import SlackNormalizer
from integrations.slack.discovery import SlackDiscovery
from integrations.slack.extractors.messages import SlackMessageExtractor

class SlackSyncService:
    """Orchestrates Slack Discovery (Mod 2) and Conversation Intelligence (Mod 3)."""
    
    def __init__(self, client):
        self.client = client
        self.discovery = SlackDiscovery(client)
        self.message_extractor = SlackMessageExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Slack Sync Service] Starting Enterprise Workspace Sync...")
        
        # MODULE 2: Workspace Discovery
        channels = await self.discovery.fetch_channels()
        user_map = await self.discovery.fetch_users()
        
        all_normalized_events = []
        
        # MODULE 3: Conversation Intelligence
        for channel in channels:
            chan_id = channel["id"]
            chan_name = channel["name"]
            
            # 1. Fetch raw messages
            raw_messages = await self.message_extractor.fetch_channel_history(chan_id, limit=30)
            
            # 2. Add real human names instead of IDs
            enriched_messages = self.message_extractor.enrich_messages_with_users(raw_messages, user_map)
            
            incident_svc = SlackIncidentService(self.client)
            convo_svc = SlackConversationService(self.client)

            # Specific channel ID milne ke baad call mar lo
            incidents = await incident_svc.detect_active_incidents(chan_id, chan_name)
            # 3. Handle Threads & Normalize
            for msg in enriched_messages:
                # If message is the start of a thread, fetch the whole thread
                thread_ts = msg.get("thread_ts")
                full_text = msg.get("text", "")
                
                if thread_ts and thread_ts == msg.get("ts"):
                    replies = await self.message_extractor.fetch_thread_replies(chan_id, thread_ts)
                    # Combine thread text for the AI context (Module 11/12 Prep)
                    reply_texts = [r.get("text", "") for r in replies if r.get("ts") != thread_ts]
                    if reply_texts:
                        full_text += "\n\n--- Thread Replies ---\n" + "\n".join(reply_texts)
                        msg["text"] = full_text # Overwrite with full context
                
                # Normalize to UniversalEvent
                normalized = SlackNormalizer.normalize_message(msg, chan_name)
                all_normalized_events.append(normalized)
                    
        print(f"🧠 [AgentOS Brain] Normalized {len(all_normalized_events)} total rich events from Slack!")
        return all_normalized_events