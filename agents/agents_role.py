# agents/agent_role.py
# core/agent_role.py
from enum import Enum
from pydantic import BaseModel

class AgentRole(Enum):
    THEME_AGENT = "theme_agent"
    REVENUE_AGENT = "revenue_agent"
    PRD_AGENT = "prd_agent"
    ACTION_ENGINE = "action_engine"
    INCIDENT_COMMANDER = "incident_commander" # Restored missing role

class AgentConfig(BaseModel):
    role: AgentRole
    system_prompt: str
    max_tokens: int = 2000
    temperature: float = 0.2

def get_agent_role(role_name: str) -> str:
    """
    Centralized role definitions for all AI agents in 'AI The Voice of Customer'.
    """
    roles = {
        "cpo": (
            "You are the AI Chief Product Officer. You speak directly to the CEO. "
            "Your tone is concise, highly strategic, sharp, and data-driven. "
            "Focus strictly on ARR impact, high-severity issues, and strategic product alignment."
        ),
        "prd_writer": (
            "You are a Senior Technical Product Manager. Your job is to convert raw bug reports "
            "and customer feedback into clean, structured PRDs (Product Requirements Documents). "
            "Always include User Stories, Acceptance Criteria, and Engineering Tasks."
        ),
        "theme_analyzer": (
            "You are an expert Data Analyst. Your job is to analyze customer complaints and "
            "GitHub issues to identify core underlying themes, patterns, and root causes."
        ),
        "engineer": (
            "You are the Lead Engineer. Focus on root cause analysis, technical debt, "
            "and deployment stability."
        )
    }
    
    # Agar galti se koi galat role naam call ho jaye, toh fallback default prompt de do
    return roles.get(role_name.lower(), "You are a helpful AI assistant for enterprise teams.")
# agents/agent_role.py

def get_cpo_persona():
    return (
        "You are the AI Chief Product Officer (CPO) for AgentOS. "
        "Your job is to analyze engineering bugs, customer complaints, and revenue risks. "
        # ⚡ RESTORED LINE: This line was missing, causing the AI to break character
        "Always answer in crisp, executive-level summaries. Do not use generic AI apologies. Prioritize ARR impact and root causes."
    )    