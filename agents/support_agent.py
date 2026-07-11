import os
from groq import AsyncGroq
from dotenv import load_dotenv

load_dotenv()
groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

async def normalize_support_ticket(raw_text: str) -> str:
    print("🌍 [Support Agent] Translating and extracting core technical issue...")
    
    prompt = f"""
    You are an enterprise AI Support Normalizer for AgentOS.
    Analyze the following raw customer ticket (which may be in any language or highly emotional).
    Your task:
    1. Translate to English if it's in another language.
    2. Strip away all emotions, greetings, and irrelevant rants.
    3. Extract ONLY the core technical bug/issue.
    
    Raw Ticket: "{raw_text}"
    
    Return ONLY the clean, technical description. No conversational filler.
    """
    
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1 # Keep it strictly factual
        )
        clean_issue = response.choices[0].message.content.strip()
        print(f"      ↳ [Support Agent] Normalized output: {clean_issue[:50]}...")
        return clean_issue
    except Exception as e:
        print(f"🚨 [Support Agent Error] Translation failed: {str(e)}")
        # Fallback to raw text if LLM fails
        return raw_text

# agents/support_agent.py ke end mein yeh add karo:

async def normalize_support_ticket(raw_text: str, *args, **kwargs):
    """
    MVP: Translates emotional customer support text into a clean technical issue.
    """
    print("🎧 [Support Agent] Normalizing customer ticket into technical format...")
    # For MVP, we just pass the text. Later, Groq LLM will summarize this.
    return f"Normalized Technical Issue: {raw_text}" 
async def translate_customer_ticket(raw_text: str, *args, **kwargs):
    """
    MVP: Translates raw customer support complaints into technical issues.
    """
    print("🗣️ [Support Agent] Translating customer text into technical bug...")
    
    # For MVP, returning a simple formatted string.
    # In production, Groq LLM will extract the exact technical root cause here.
    return f"Customer reported: {raw_text} -> Requires engineering review."           