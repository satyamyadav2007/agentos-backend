from sqlalchemy import Column, String, DateTime
from datetime import datetime
import uuid
from database.postgres_setup import Base

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