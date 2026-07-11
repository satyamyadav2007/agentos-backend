# integrations/schema.py
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class UniversalEvent(BaseModel):
    """The central nervous system schema for AgentOS"""
    source: str = Field(..., description="e.g., github, slack, zendesk")
    entity_type: str = Field(..., description="e.g., issue, pull_request, commit, release")
    repository: Optional[str] = None
    title: str
    description: Optional[str] = None
    author: str
    severity: str = Field(default="Unknown", description="Critical, High, Medium, Low")
    timestamp: datetime
    metadata: Dict[str, Any] = Field(default_factory=dict) # Raw specific data goes here
    
    # ⚡ Link to Neo4j Knowledge Graph
    linked_entities: list[str] = Field(default_factory=list, description="IDs of related PRs, commits, or tickets")