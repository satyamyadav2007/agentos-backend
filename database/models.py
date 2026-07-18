
from datetime import datetime
import uuid
from database.postgres_setup import Base
from sqlalchemy import Column, Integer, String, JSON, DateTime, Boolean
from sqlalchemy.sql import func


def generate_enterprise_id(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: generate_enterprise_id("usr"))
    clerk_id = Column(String, unique=True, index=True) # Clerk se aane wala 'sub'
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(String, primary_key=True, default=lambda: generate_enterprise_id("ws"))
    org_id = Column(String, index=True, default=lambda: generate_enterprise_id("org"))
    name = Column(String, index=True)
    industry = Column(String)
    size = Column(String)
    region = Column(String)
    owner_clerk_id = Column(String, index=True) # Jisne banaya
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkspaceIntegration(Base):
    """Stores GitHub App installations and tokens for workspaces."""
    __tablename__ = "workspace_integrations"

    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(String, index=True, nullable=False)
    provider = Column(String, index=True, nullable=False) # e.g., "github"
    installation_id = Column(String, nullable=True) 
    account_name = Column(String, nullable=True)
    access_token = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UniversalEventRecord(Base):
    """Stores the normalized data strictly following the AgentOS contract."""
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