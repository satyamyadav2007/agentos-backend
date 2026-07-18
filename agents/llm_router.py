import os
from openai import AsyncOpenAI
from dotenv import load_dotenv


load_dotenv()

async def call_cloud_llm(prompt: str, system_prompt: str = "You are an expert AI CPO for AgentOS.") -> str:
    """
    Calls a reliable, ultra-fast cloud LLM via Groq using the OpenAI SDK.
    """
    # ⚡ Using Groq for stable, lightning-fast free inference
    api_key = os.getenv("GROQ_API_KEY") 
    if not api_key:
        print("🚨 [LLM Router] GROQ_API_KEY missing! Check .env file.")
        return '{"category": "System Error", "severity": "High", "summary": "API Key missing.", "requires_prd": false}'

    # Pointing the OpenAI client to Groq's servers
    client = AsyncOpenAI(
        base_url="https://api.groq.com/openai/v1",
        api_key=api_key,
    )

    print(f"⚡ [LLM Router] Routing task to Groq Cloud (Ultra-Fast & Stable)...")
    
    try:
        # Using the official stable Llama 3 8B model on Groq
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"❌ [LLM Router] Failed to contact Cloud LLM: {str(e)}")
        return '{"category": "System Error", "severity": "High", "summary": "API call failed.", "requires_prd": false}'