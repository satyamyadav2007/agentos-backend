from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func
# Ye import wahi se hoga jahan tumne Source 7 wala code rakha hai (e.g., database.py)
from database import Base 

class WorkspaceIntegration(Base):
    """Stores GitHub App installations and tokens for workspaces."""
    __tablename__ = "workspace_integrations"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String, index=True, nullable=False)
    provider = Column(String, index=True, nullable=False) # e.g., "github"
    installation_id = Column(String, nullable=True) # Webhook se aayega
    account_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UniversalEventRecord(Base):
    """Stores the normalized data (Sprint 1 - Module 20)"""
    __tablename__ = "universal_events"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String, index=True, nullable=False)
    source = Column(String, index=True) # "github", "jira"
    entity_type = Column(String, index=True) # "issue", "pull_request"
    repository = Column(String, index=True)
    title = Column(String)
    severity = Column(String, index=True) # AI-driven severity
    author = Column(String)
    metadata_json = Column(JSON) # Labels, URLs, etc.
    created_at = Column(DateTime(timezone=True), server_default=func.now())