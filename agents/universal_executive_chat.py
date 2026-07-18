import os
import json
from groq import AsyncGroq
from typing import Dict, Any

from agents.llm_router import call_cloud_llm # Apne router ka path dena
from database.graph_manager import graph_db

class UniversalExecutiveAgent:
    """
    ONE AGENT TO RULE THEM ALL (30+ Tools Supported).
    Fuses Dashboard Context (ARR/Risk) with GraphDB (Root Cause Tracing).
    """
    
    def __init__(self):
        # Initiating Groq client from the Root Cause logic
        self.llm = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY")) #[cite: 4]

    async def _extract_entity(self, user_message: str) -> str:
        """Micro-agent to extract the core keyword (e.g., ticket key, sprint) to search the Graph."""
        prompt = f"Extract the core entity/keyword from this query. Return ONLY the string. If none, return 'GLOBAL'. Query: {user_message}"
        try:
            res = await call_cloud_llm(prompt=prompt, system_prompt="Strict text extractor.")
            return res.strip()
        except:
            return "GLOBAL"

    async def analyze_and_chat(self, user_message: str, dashboard_context: list) -> Dict[str, Any]:
        print(f"💬 [Universal Chat] Analyzing executive query: '{user_message}'") #[cite: 3]
        
        # ==========================================
        # 1. PARSE DASHBOARD METRICS (From Chat Agent)
        # ==========================================
        context_str = "CURRENT DASHBOARD METRICS (Source of Truth):\n" #[cite: 3]
        total_risk = 0 #[cite: 3]
        
        if dashboard_context: #[cite: 3]
            for item in dashboard_context: #[cite: 3]
                title = item.get("originalText", "Unknown Issue") #[cite: 3]
                risk = item.get("revenue", {}).get("revenue_at_risk", 0) #[cite: 3]
                severity = item.get("analysis", {}).get("severity", "Unknown") #[cite: 3]
                total_risk += risk #[cite: 3]
                context_str += f"- Bug: {title} | Severity: {severity} | Revenue Risk: ${risk}\n" #[cite: 3]
        else:
            context_str += "- No active issues reported on the dashboard currently.\n" #[cite: 3]
            
        context_str += f"\nTOTAL REVENUE AT RISK: ${total_risk}\n\n" #[cite: 3]

        # ==========================================
        # 2. TRACE ROOT CAUSE IN GRAPHDB (From Root Cause Agent)
        # ==========================================
        issue_keyword = await self._extract_entity(user_message)
        graph_data_str = "No connected graph data found."
        
        if issue_keyword != "GLOBAL":
            print(f"🧠 [Root Cause Agent] Analyzing graph for: {issue_keyword}") #[cite: 4]
            # Fetches Traced Data from Neo4j Knowledge Graph (Works for Jira, GitHub, Slack, etc.)
            graph_data = graph_db.get_root_cause_context(issue_keyword) #[cite: 4]
            if graph_data: #[cite: 4]
                graph_data_str = json.dumps(graph_data, indent=2) #[cite: 4]

        # ==========================================
        # 3. UNIFIED CPO SYSTEM PROMPT
        # ==========================================
        system_prompt = f"""You are AgentOS, the AI Chief Product Officer. #[cite:3, 4]
        You are speaking directly to the CEO. Tone: Highly strategic, ruthless, data-driven, and extremely concise. #[cite: 3]
        
        KNOWLEDGE BASE (Dashboard):
        {context_str} #[cite: 3]
        
        TRACED GRAPH DATA (Root Cause across 30+ tools):
        {graph_data_str}
        
        RULES:
        1. Always base your answers on the KNOWLEDGE BASE and TRACED GRAPH DATA provided above. #[cite: 3]
        2. Do not hallucinate metrics, bugs, or engineer names. If data is missing, state it clearly. #[cite: 3]
        3. If Graph data is present, provide an executive-level Root Cause Summary including: #[cite: 4]
           - The Core Bug/Issue. #[cite: 4]
           - The Responsible Engineer (if identified). #[cite: 4]
           - The status of the Fixing Pull Request (PR) or Commit. #[cite: 4]
           - Next actionable step. #[cite: 4]
        4. If the user asks about revenue at risk, analyze it and provide a strategic recommendation. #[cite: 3]
        5. Keep answers under 4 sentences. Bullet points are encouraged for readability. #[cite: 3]
        6. Do not use filler words. Be factual and direct. #[cite: 4]
        """

        # ==========================================
        # 4. LLM EXECUTION
        # ==========================================
        try:
            # Using the strict configuration from RootCauseAgent for precise factual answers
            completion = await self.llm.chat.completions.create( #[cite: 4]
                messages=[ #[cite: 4]
                    {"role": "system", "content": system_prompt}, #[cite: 4]
                    {"role": "user", "content": user_message}
                ],
                model="llama-3.1-8b-instant", #[cite: 4]
                temperature=0.2, # Strict & Factual #[cite: 4]
            )
            
            ai_reply = completion.choices[0].message.content #[cite: 4]
            
            return {
                "status": "success", #[cite:3, 4]
                "keyword_traced": issue_keyword,
                "reply": ai_reply.strip() #[cite: 3]
            }
            
        except Exception as e:
            print(f"🚨 [Universal Executive Error]: {e}")
            return {"status": "error", "reply": "System Error: Neural link severed."} #[cite: 3]

# Global Instance
universal_executive_chat = UniversalExecutiveAgent()