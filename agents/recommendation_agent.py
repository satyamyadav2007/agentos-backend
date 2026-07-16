import os
import json
from groq import AsyncGroq
from database.graph_manager import graph_db

class RecommendationAgent:
    """Module 18: Generates actionable AI insights for Revenue, Engineering, and Churn."""
    
    def __init__(self):
        self.llm = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY"))

    async def generate_recommendations(self, user_email: str) -> dict:
        print(f"💡 [Recommendation Engine] Synthesizing AI advice for {user_email}...")
        
        # 1. Fetch real context from your Knowledge Graph
        active_issues = graph_db.get_active_issues(user_email, limit=3)
        causal_insights = graph_db.get_causal_insights()
        
        # 2. Strict AI Prompt designed for JSON Output
        prompt = f"""
        You are AgentOS, an elite AI Chief Product Officer.
        Based on the current system health, generate 3 highly actionable, ruthless recommendations.
        
        CONTEXT FROM NEO4J GRAPH:
        Active Critical Issues: {active_issues}
        Causal Insights (Revenue/Churn): {causal_insights}
        
        OUTPUT FORMAT (Strict JSON):
        {{
          "revenue": {{ "title": "Short Action (e.g., Merge PR #841)", "subtitle": "Reason", "value": "Impact (e.g., $120k)" }},
          "engineering": {{ "title": "Short Action (e.g., Rollback v4.8)", "subtitle": "Reason", "value": "Impact (e.g., -20% crashes)" }},
          "churn": {{ "title": "Short Action (e.g., Call Acme Corp)", "subtitle": "Reason", "value": "Urgency (e.g., 48 Hours)" }}
        }}
        
        Respond ONLY with a valid JSON object. Do not include markdown formatting or explanations.
        """
        
        try:
            completion = await self.llm.chat.completions.create(
                messages=[{"role": "system", "content": prompt}],
                model="llama-3.1-8b-instant",
                temperature=0.2, # Low temperature for logical consistency
                response_format={"type": "json_object"} # ⚡ Force JSON output
            )
            
            ai_suggestions = json.loads(completion.choices[0].message.content)
            print("   ✅ AI Recommendations generated successfully.")
            return ai_suggestions
            
        except Exception as e:
            print(f"🚨 [Recommendation Engine Error]: {e}")
            # Safe Fallback
            return {
                "revenue": { "title": "Analyze Revenue Model", "subtitle": "System scanning...", "value": "TBD" },
                "engineering": { "title": "Review Recent Commits", "subtitle": "System scanning...", "value": "TBD" },
                "churn": { "title": "Monitor Active Users", "subtitle": "System scanning...", "value": "TBD" }
            }

# Global Instance
recommendation_engine = RecommendationAgent()