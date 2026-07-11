from .llm_router import call_cloud_llm
import json

class ThemeAgent:
    async def analyze_theme(self, text: str):
        print("[Theme Agent] Analyzing text with Cloud LLM...")
        
        system_prompt = """
        You are an AI Product Strategist. Analyze the following user feedback.
        Categorize it into one of these: 'Bug', 'Feature Request', 'Pricing', or 'Churn Risk'.
        Estimate the severity: 'High', 'Medium', or 'Low'.
        Write a 1-sentence summary.
        
        IMPORTANT: You must return ONLY a raw JSON object. Do not add markdown formatting or extra text.
        Format exactly like this:
        {"category": "Bug", "severity": "High", "summary": "brief summary here", "requires_prd": true}
        """
        
        try:
            # ⚡ Calling Cloud LLM via router (Zero local RAM usage)
            raw_output = await call_cloud_llm(prompt=text, system_prompt=system_prompt)
            raw_output = raw_output.strip()
            
            # Parse output safely
            if raw_output.startswith("```json"):
                raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            elif raw_output.startswith("```"):
                raw_output = raw_output.replace("```", "").strip()
                
            theme_data = json.loads(raw_output)
            return theme_data
            
        except json.JSONDecodeError:
            print("[Error] Model didn't return valid JSON. Fallback triggered.")
            return {
                "category": "Unclassified",
                "severity": "Unknown",
                "summary": "AI failed to parse the text.",
                "requires_prd": False,
                "raw_text": raw_output
            }
        except Exception as e:
            print(f"[Error] Theme Agent failed: {e}")
            raise e