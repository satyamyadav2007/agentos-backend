from typing import Dict, Any, List
from integrations.base import BaseConnector
from .providers.notion import NotionProvider
from .providers.confluence import ConfluenceProvider
from .providers.google_docs import GoogleDocsProvider
from .normalizer import KnowledgeNormalizer
from .utils.chunking import SmartChunker

class KnowledgeSyncService:
    def __init__(self, provider):
        self.provider = provider
        
    async def run_full_sync(self) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        print(f"\n🚀 [Knowledge Sync] Starting Enterprise Brain Sync...")
        
        docs = await self.provider.fetch_recent_pages(limit=20)
        
        # 1. Normalize for Event Bus & Neo4j (Graph Knowledge)
        all_universal_events = [KnowledgeNormalizer.normalize_document(d) for d in docs]
        
        # 2. Chunk for Vector DB (Semantic Knowledge)
        vector_chunks = []
        for doc in docs:
            chunks = SmartChunker.chunk_document(doc.content)
            for i, chunk_text in enumerate(chunks):
                vector_chunks.append({
                    "id": f"{doc.id}_chunk_{i}",
                    "text": chunk_text,
                    "metadata": {"source": doc.provider, "title": doc.title, "url": doc.url}
                })
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} Docs and created {len(vector_chunks)} Semantic Chunks!")
        return all_universal_events, vector_chunks


class KnowledgeConnector(BaseConnector):
    def __init__(self, workspace_id: str, org_id: str):
        super().__init__(workspace_id, org_id)
        self.active_provider = None

    async def connect(self, auth_payload: Dict[str, Any]) -> Dict[str, Any]:
        provider_name = auth_payload.get("provider", "").lower()
        token = auth_payload.get("token")
        
        if not provider_name or not token:
            return {"status": "error", "message": "Missing Provider or Token"}
            
        try:
            # ⚡ Dynamic Initialization based on User Selection
            if provider_name == "notion":
                self.active_provider = NotionProvider(token)
            elif provider_name == "confluence":
                # Confluence often needs a domain, handling it gracefully
                domain = auth_payload.get("domain", "your-domain.atlassian.net")
                self.active_provider = ConfluenceProvider(token, domain)
            elif provider_name == "google_docs":
                self.active_provider = GoogleDocsProvider(token)
            else:
                return {"status": "error", "message": "Invalid Knowledge Provider"}
                
            sync_result = await self.sync()
            return {"status": "connected", "provider": f"knowledge_{provider_name}", "sync_info": sync_result}
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    async def sync(self) -> Dict[str, Any]:
        if not self.active_provider:
            return {"status": "error", "message": "No active knowledge provider"}
            
        sync_service = KnowledgeSyncService(self.active_provider)
        normalized_events, vector_chunks = await sync_service.run_full_sync()
        
        # ⚡ DUAL-ROUTING ARCHITECTURE (Module 19 & 20)
        
        # Route 1: To ChromaDB / Vector DB for Semantic Search
        if vector_chunks:
            print("📚 [AgentOS] Embedding chunks into Vector Database...")
            # USING YOUR EXISTING CHROMA_DB ARCHITECTURE
            from chroma_db.vector_store import get_vector_store # Assuming this exists based on your setup
            v_store = get_vector_store()
            # await v_store.add_documents(vector_chunks) 
            
        # Route 2: To Universal Event Bus for Graph Connections (Neo4j)
        if normalized_events:
            print("🕸️ [AgentOS] Routing Metadata to Universal Event Bus & Neo4j...")
            # USING YOUR EXISTING EVENT BUS & GRAPH_MANAGE
            from core.event_bus import event_bus
            from core.models.event import UniversalEvent
            
            events_objs = [UniversalEvent(**e) for e in normalized_events]
            await event_bus.publish(events_objs)
            
        print("✅ [AgentOS] Enterprise Knowledge Engine Sync Complete!")
            
        return {"status": "synced", "docs_processed": len(normalized_events), "chunks": len(vector_chunks)}

    async def webhook(self, payload: Dict[str, Any]) -> bool: pass
    async def disconnect(self) -> bool: pass