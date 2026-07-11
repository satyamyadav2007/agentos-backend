from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class KnowledgeDocumentModel(BaseModel):
    id: str
    provider: str  # 'notion', 'confluence', 'google_docs'
    title: str
    content: str
    author: str
    url: str
    created_at: datetime
    updated_at: datetime
    space_or_folder: Optional[str] = "Workspace"
    
    @property
    def is_architecture_or_prd(self) -> bool:
        """AI Heuristic: Detects highly critical core documents."""
        keywords = ["prd", "architecture", "rfc", "design doc", "system"]
        return any(k in self.title.lower() for k in keywords)