import os
import json
from groq import AsyncGroq
from database.graph_manager import graph_db

class RootCauseAgent:
    """Module 10: Deep Graph Analysis to find the root cause of issues."""
    
    def __init__(self):
        self.llm = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

    async def analyze_issue(self, issue_keyword: str) -> dict:
        print(f"🧠 [Root Cause Agent] Analyzing graph for: {issue_keyword}")
        
        # 1. Fetch Traced Data from Neo4j Knowledge Graph
        graph_data = graph_db.get_root_cause_context(issue_keyword)
        
        if not graph_data:
            return {
                "status": "error",
                "message": f"No connected graph data found for '{issue_keyword}'."
            }

        # 2. Strict AI Prompt
        prompt = f"""
        You are AgentOS, the AI Chief Product Officer. 
        Analyze this traced data from our Neo4j Engineering Knowledge Graph regarding '{issue_keyword}':
        
        {json.dumps(graph_data, indent=2)}
        
        Provide a highly concise, executive-level Root Cause Summary.
        Include:
        1. The Core Bug/Issue.
        2. The Responsible Engineer (if identified).
        3. The status of the Fixing Pull Request (PR) or Commit.
        4. Next actionable step.
        
        Do not use filler words. Be factual and direct.
        """

        try:
            completion = await self.llm.chat.completions.create(
                messages=[{"role": "system", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.2, # Strict & Factual
            )
            
            ai_summary = completion.choices[0].message.content
            
            return {
                "status": "success",
                "keyword": issue_keyword,
                "summary": ai_summary,
                "raw_graph_data": graph_data
            }
            
        except Exception as e:
            print(f"🚨 [Root Cause Agent Error]: {e}")
            return {"status": "error", "message": str(e)}

# Global Instance
root_cause_engine = RootCauseAgent()