from typing import Dict, Any
from .models.document import KnowledgeDocumentModel

class KnowledgeNormalizer:
    
    @staticmethod
    def normalize_document(doc: KnowledgeDocumentModel) -> Dict[str, Any]:
        """Converts a Knowledge Doc into an AgentOS UniversalEvent for the Graph DB."""
        
        severity = "High" if doc.is_architecture_or_prd else "Low"

        return {
            "source": f"knowledge_{doc.provider}",
            "entity_type": "document",
            "repository": doc.space_or_folder,
            "title": doc.title,
            "description": doc.content[:1000], # Keep a snippet for Graph DB context
            "author": doc.author,
            "severity": severity,
            "timestamp": doc.updated_at.isoformat(),
            "metadata": {
                "doc_id": doc.id,
                "url": doc.url,
                "provider": doc.provider
            },
            # Graph Connections! Module 5: Connect PRD to Features & API Endpoints
            "linked_entities": [] 
        }