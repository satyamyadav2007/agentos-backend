import os
import json
from groq import AsyncGroq

# Groq client for ultra-fast parsing
groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY", "fallback_key"))

async def normalize_universal_signal(source: str, raw_data: str) -> dict:
    print(f"\n🌪️ [Normalizer Agent] Ingesting messy raw data from {source}...")
    
    # The Master Prompt: Forcing the LLM to act as a Data Parser
    prompt = f"""You are the AgentOS Universal Data Normalizer.
    Your job is to read messy, unstructured data from {source} (like crash logs, Zoom transcripts, Reddit posts, or CRMs) and convert it into a strict, standardized JSON format.
    
    RAW DATA: {raw_data}
    
    Respond STRICTLY with a JSON object containing EXACTLY these keys:
    - "title": A crisp 5-7 word summary of the signal.
    - "description": A clear explanation of the issue, feedback, or insight.
    - "sentiment": Classify as "Positive", "Neutral", "Negative", or "Angry".
    - "severity": Classify as "Low", "Medium", "High", or "Critical".
    - "entities": A list of important keywords (e.g., specific features, error codes, company names, or people mentioned).
    
    Do not output any markdown formatting, no explanations, ONLY valid JSON.
    """
    
    try:
        response = await groq_client.chat.completions.create(
            messages=[{"role": "system", "content": prompt}],
            model="llama3-8b-8192", # Fast and reliable for JSON structuring
            temperature=0.1 # Very low temp for strict JSON output
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Safety filter: Clean markdown tags if LLM accidentally adds them
        if result_text.startswith("```json"):
            result_text = result_text[7:-3]
        elif result_text.startswith("```"):
            result_text = result_text[3:-3]
            
        normalized_data = json.loads(result_text)
        normalized_data["source"] = source # Tagging the origin
        
        print(f"✅ [Normalizer Agent] Standardized {source} signal! Severity: {normalized_data['severity']}")
        return normalized_data
        
    except Exception as e:
        print(f"🚨 [Normalizer Error] Failed to parse data: {e}")
        # Fallback mechanism so the pipeline doesn't crash
        return {
            "title": f"Raw {source} Signal",
            "description": str(raw_data)[:500],
            "sentiment": "Neutral",
            "severity": "Medium",
            "source": source,
            "entities": []
        }