# agents/theme_agent.py
import json
from ollama import AsyncClient

async def extract_theme(text: str):
    print("[Theme Agent] Analyzing text with local Llama 3...")
    
    # Prompt engineering specifically for open-source models
    # Hum model ko strictly JSON return karne ko bol rahe hain
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
        # Calling Ollama running locally on your laptop
        response = await AsyncClient().chat(
            model='llama3', # Ya 'mistral' agar tumne wo download kiya hai
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': text}
            ],
            options={
                "temperature": 0.1 # Low temperature for more deterministic/factual output
            }
        )
        
        # Extracting the text response from the model
        raw_output = response['message']['content'].strip()
        
        # Parsing the string into an actual Python dictionary (JSON)
        # We try to clean it just in case the model added markdown blocks
        if raw_output.startswith("```json"):
            raw_output = raw_output.replace("```json", "").replace("```", "").strip()
            
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