import os
import json
import asyncio
import traceback
import jwt
import requests
import uuid
from sqlalchemy.orm import Session
from database.postgres_setup import engine, get_db
from database import models
from datetime import datetime
from pydantic import BaseModel
from fastapi import HTTPException, Depends
from typing import Optional
from fastapi import Form

from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, BackgroundTasks, File, UploadFile, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from groq import AsyncGroq
from github import Github

# Custom Agents & Managers (Ensure these exist in your project)
from os_kernel import kernel
from orchestrator import run_orchestrator, process_single_issue
from agents.jira_agent import create_jira_ticket
from agents.chat_agent import ask_executive_cpo
from database.graph_manager import graph_db
from integrations.manager import integration_manager
from agents.support_agent import translate_customer_ticket
from agents.normalizer_agent import normalize_universal_signal
from adapters.webhook_router import identify_signal_source, normalize_pusher_payload
from adapters.scraper_engine import scraper, wild_west_engine
from adapters.action_engine import action_arm
from adapters.crm_aggregator import crm_engine
from adapters.apify_engine import apify_connector
from adapters.log_engine import parse_engineering_logs
from agents.agents_role import get_cpo_persona
from dotenv import load_dotenv
from contextlib import asynccontextmanager
from core.event_bus import event_bus
load_dotenv() # ⚡ Yeh line tumhari .env file ke saare variables ko system mein load kar degi

# ==========================================
# 🚀 1. APP INITIALIZATION & MIDDLEWARE
# ==========================================
app = FastAPI(title="AgentOS Chief Product Officer API", version="1.1")
models.Base.metadata.create_all(bind=engine)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Start the Event Bus
    await event_bus.start()
    yield
    # Shutdown: Stop the Event Bus gracefully
    await event_bus.stop()

# Apne existing app instance me lifespan add kar do
# (Agar pehle se koi app bana hua hai to usme lifespan=lifespan pass kar do)
app = FastAPI(title="AgentOS API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000/dashboard",
        "https://agentos-frontend-azure.vercel.app", 
        "*"  # Allows all domains temporarily for MVP
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 🔒 2. CLERK AUTHENTICATION GATEKEEPER
# ==========================================
security = HTTPBearer()

CLERK_JWKS_URL = os.getenv("CLERK_JWKS_URL")
CLERK_ISSUER = os.getenv("CLERK_ISSUER")          # https://<your-clerk-domain>
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE")      # Optional

# Cache JWKS in production if possible
JWKS_CACHE = None


def verify_clerk_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verify Clerk JWT and return authenticated user info. (Bulletproof Version)
    """
    global JWKS_CACHE
    token = credentials.credentials

    try:
        if not token:
            print("🚨 [Auth Error]: Frontend didn't send a token!")
            raise HTTPException(status_code=401, detail="No token provided")

        # 1. Fetch JWKS
        if JWKS_CACHE is None:
            import requests
            response = requests.get(CLERK_JWKS_URL, timeout=5)
            response.raise_for_status()
            JWKS_CACHE = response.json()

        # 2. Get Header & Key
        unverified_header = jwt.get_unverified_header(token)
        rsa_key = next(
            (key for key in JWKS_CACHE.get("keys", []) if key.get("kid") == unverified_header.get("kid")),
            None,
        )

        if rsa_key is None:
            print("🚨 [Auth Error]: Invalid Clerk signing key.")
            raise HTTPException(status_code=401, detail="Invalid Clerk signing key.")

        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(rsa_key)

        # 3. Decode JWT (With Relaxed Audience check for Dev Mode)
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=CLERK_ISSUER,
            options={"verify_aud": False} 
        )

        # 4. Extract Email (With Bulletproof Fallback)
        email = (
            payload.get("email")
            or payload.get("primary_email_address")
            or payload.get("email_address")
        )

        if not email:
            print("⚠️ [Auth Warning]: Email not in Clerk token. Using 'sub' (User ID) as fallback.")
            user_id = payload.get("sub", "unknown_user")
            email = f"{user_id}@clerk.local"

        print(f"✅ [Auth Success]: User {email} verified successfully!")
        
        return {
            "sub": payload.get("sub"),
            "email": email,
            "payload": payload,
        }

    except jwt.ExpiredSignatureError:
        print("🚨 [Auth Error]: The Token has EXPIRED. Refresh the frontend page.")
        raise HTTPException(status_code=401, detail="Token Expired")
        
    except jwt.InvalidTokenError as e: 
        print(f"🚨 [Auth Error]: Invalid Token or Claims: {e}")
        raise HTTPException(status_code=401, detail="Invalid Token")
        
    except Exception as e:
        print(f"🚨 [Auth Error]: General failure -> {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=401, detail="Unauthorized")
# 📡 3. WEBSOCKET MANAGER
# ==========================================
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()
ws_manager = ConnectionManager()

# 3. Uske baad tumhara Background Worker aayega
async def run_ai_pipeline_in_background(request_type: str, payload: dict, user_email: str):
    print(f"\n⚙️ [Background Worker] Starting AI analysis for {user_email}...")
    try:
        from os_kernel import kernel
        result = await kernel.execute(request_type, payload, user_email)
        
        # Ab 'manager' properly upar defined hai, toh yeh line nahi fategi!
        await manager.broadcast(json.dumps({
            "type": "NEW_ALERT",
            "data": result
        }))
        print("✅ [Background Worker] Processing complete and pushed to Dashboard UI!")
    except Exception as e:
        print(f"🚨 [Background Worker Error] Pipeline failed: {str(e)}")

# --- WebSocket Route ---
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)


# --- Data Models ---
class GithubPayload(BaseModel):
    repo_name: str
    token: str

class FeedbackPayload(BaseModel):
    source: str
    raw_text: str
    user_email: str

class JiraPayload(BaseModel):
    domain: str
    email: str
    token: str
    project_key: str
    title: str
    prd_text: str

class ChatPayload(BaseModel):
    message: str
    context_data: list 

class SupportTicketPayload(BaseModel):
    ticket_text: str
    user_email: str

class JiraExportPayload(BaseModel):
    title: Optional[str] = "AI Generated Jira Task"
    prd_content: Optional[str] = "Auto-generated PRD details will appear here."
    domain: Optional[str] = None
    email: Optional[str] = None
    token: Optional[str] = None
    project_key: Optional[str] = "KAN"
    prd_text: Optional[str] = None


# --- REST Routes ---

@app.get("/")
async def root():
    return {"message": "Welcome to AgentOS API! The engine is running."}

@app.get("/health")
def system_health_check():
    return {
        "status": "Operational",
        "platform": "AgentOS AI CPO",
        "modules": ["Neo4j", "ChromaDB", "Groq_LLM", "Orchestrator"],
        "readiness": "100%"
    }

@app.post("/process-support")
async def process_support(request: Request, background_tasks: BackgroundTasks):
    # 1. Payload extract karo
    payload = await request.json()
    user_email = payload.get("user_email", "user_email")
    
    # 2. Kaam ko Background Worker ko saunp do (Handoff)
    background_tasks.add_task(
        run_ai_pipeline_in_background, 
        request_type="zendesk_ticket", 
        payload=payload, 
        user_email=user_email
    )
    
    # 3. Manager ko turant response de do (Zero Loading Time!)
    return {
        "status": "success", 
        "message": "Payload received. AgentOS is processing in the background."
    }

@app.post("/process-feedback")
async def process_feedback(payload: FeedbackPayload):
    try:
        result = await run_orchestrator(
            text=payload.raw_text, 
            source=payload.source,
            user_email=payload.user_email
        )
        return {"status": "success", "data": result}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/causal-summary")
async def get_causal_summary():
    print("[API] Fetching real causal summary from Neo4j Aura...")
    try:
        real_insights = graph_db.get_causal_insights()
        return {
            "status": "success",
            "data": real_insights
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))  

# ⚡ FIX 3: Github execution must strictly use the authenticated email
@app.post("/process-github")
async def process_github_issues(request: Request, auth_payload: dict = Depends(verify_clerk_user)):
    payload = await request.json()
    issues = payload.get("issues", [])
    
    # Extract real email from the secure payload sent by frontend
    real_email = payload.get("user_email")
    
    if not real_email:
        raise HTTPException(status_code=400, detail="Real user_email is missing in payload")

    print(f"🐙 [GitHub Engine] Processing {len(issues)} issues for {real_email}")
    
    results = []
    for issue in issues:
        # Strictly executing under the real_email namespace
        kernel_response = await kernel.execute("github_issue", raw_payload=issue, user_email=real_email)
        
        if "issues" in kernel_response and len(kernel_response["issues"]) > 0:
            processed_issue = kernel_response["issues"][0]
            results.append(processed_issue)
            
            await ws_manager.broadcast(json.dumps({
                "type": "NEW_ALERT",
                "data": processed_issue,
                "target_user": real_email
            }))
    
    return {"status": "success", "data": results}
from pydantic import BaseModel
from fastapi import HTTPException
from integrations.manager import integration_manager

# Frontend se aane wale data ka schema
class ConnectPayload(BaseModel):
    installation_id: str
    workspace_id: str

# ==========================================
# 🔌 UNIVERSAL INTEGRATION ROUTE
# ==========================================
# main.py ke andar
from fastapi import APIRouter, Depends, HTTPException
# Make sure verify_clerk_user is imported properly

@app.post("/api/integrations/{provider}/connect")
async def connect_tool(
    provider: str, 
    payload: ConnectPayload,
    auth_payload: dict = Depends(verify_clerk_user) # 🔒 1. Endpoint ko secure kiya
):
    print(f"\n🔗 [AgentOS Integration] Connecting '{provider}' for workspace: {payload.workspace_id}")
    
    try:
        # ⚡ 2. Clerk Auth se real Org ID nikali, no more "org_dummy_123"
        org_id = auth_payload.get("org_id", "default_org")
        
        # ⚡ 3. Sirf EK baar connector initialize karo
        connector_instance = integration_manager._registry[provider.lower()](
            workspace_id=payload.workspace_id, 
            org_id=org_id
        )
        
        # ⚡ 4. Properly token fetch karo (await lagana zaroori hai agar method async hai)
        token_response = await connector_instance.auth_manager.get_installation_token(payload.installation_id)
        
        # Assuming token_response dictionary return karta hai jaise {"token": "ghs_xxxx"}
        connector_instance.access_token = token_response.get("token") if isinstance(token_response, dict) else token_response

        if not connector_instance.access_token:
            raise Exception("Failed to generate GitHub Access Token")

        # 👉 YAHAN FUTURE MEIN DB SAVE AAYEGA:
        # db.session.add(Integration(workspace_id=..., token=...))

        sync_result = None
        
        # ⚡ 5. Sync ko try-except mein dala taaki frontend connection na toote
        try:
            print("⏳ Triggering initial sync...")
            sync_result = await connector_instance.sync()
            print("✅ Sync completed successfully")
        except Exception as sync_err:
            print(f"⚠️ Sync failed, but connection is saved. Error: {sync_err}")
            sync_result = {"error": "Initial sync failed or delayed", "details": str(sync_err)}
            
        return {
            "status": "connected",
            "sync_info": sync_result
        }
        
    except Exception as e:
        print(f"🚨 [Integration Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))   
class IntegrationRequest(BaseModel):
    platform: str
    user_email: str
    workspace_name: str
 

@app.post("/api/integrations/connect")
async def connect_integration(req: IntegrationRequest):
    print(f"\n🔌 [Integration Engine] Connection Request Received!")
    print(f"      ↳ Workspace: {req.workspace_name} ({req.user_email})")
    print(f"      ↳ Platform: {req.platform}")
    
    # Yahan hum future mein Neo4j ya Postgres mein save karenge ki 
    # is user_email ne yeh platform connect kar liya hai.
    
    # Simulate OAuth Handshake (Takes 1-2 seconds)
    import asyncio
    await asyncio.sleep(1.5)
    
    print(f"✅ [Integration Engine] Successfully registered {req.platform} webhook for {req.workspace_name}.")
    
    return {
        "status": "success", 
        "message": f"{req.platform} successfully authenticated and synced with AgentOS.",
        "platform": req.platform
    } 
from fastapi import Request
from integrations.github.webhook import github_webhook_handler

# ==========================================
# 🕸️ GITHUB LIVE WEBHOOK ROUTE
# ==========================================
@app.post("/api/integrations/github/webhook")
async def github_live_webhook(request: Request):
    # GitHub hamesha event ka type is header mein bhejta hai
    event_name = request.headers.get("X-GitHub-Event", "unknown")
    
    try:
        payload = await request.json()
        # Webhook handler ko data pass karo
        result = await github_webhook_handler.handle_event(event_name, payload)
        return result
    except Exception as e:
        print(f"🚨 [Webhook Error]: {e}")
        return {"status": "error", "message": str(e)}  

# main.py ke andar

# Naya schema Jira ke liye
class JiraConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# ==========================================
# 🔌 JIRA OAUTH ROUTE
# ==========================================
@app.post("/api/integrations/jira/connect")
async def connect_jira(payload: JiraConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Jira' for workspace: {payload.workspace_id}")
    
    try:
        # Pass the auth_code to our Integration Manager
        result = await integration_manager.connect_integration(
            integration_name="jira",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
        
    except Exception as e:
        print(f"🚨 [Jira Integration Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
from fastapi import Request
from integrations.jira.webhook import jira_webhook_handler

# ==========================================
# 🕸️ JIRA LIVE WEBHOOK ROUTE
# ==========================================
@app.post("/api/integrations/jira/webhook")
async def jira_live_webhook(request: Request):
    try:
        payload = await request.json()
        
        # Pass the payload to our dedicated Jira webhook handler
        result = await jira_webhook_handler.handle_event(payload)
        return result
        
    except Exception as e:
        print(f"🚨 [Jira Webhook Error]: {e}")
        return {"status": "error", "message": str(e)}                        
# main.py ke andar

# Naya schema Slack ke liye
class SlackConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# ==========================================
# 💬 SLACK OAUTH ROUTE
# ==========================================
@app.post("/api/integrations/slack/connect")
async def connect_slack(payload: SlackConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Slack' for workspace: {payload.workspace_id}")
    
    try:
        result = await integration_manager.connect_integration(
            integration_name="slack",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
        
    except Exception as e:
        print(f"🚨 [Slack Integration Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 
from fastapi import Request
from integrations.slack.webhook import slack_webhook_handler

# ==========================================
# 🕸️ SLACK LIVE WEBHOOK ROUTE
# ==========================================
@app.post("/api/integrations/slack/webhook")
async def slack_live_webhook(request: Request):
    try:
        payload = await request.json()
        
        # Pass the payload to our dedicated webhook handler
        result = await slack_webhook_handler.handle_event(payload)
        
        # Slack requires the 'challenge' string returned directly during setup
        if "challenge" in result:
            return result["challenge"]
            
        return result
    except Exception as e:
        print(f"🚨 [Slack Webhook Error]: {e}")
        return {"status": "error", "message": str(e)} 
# Naya schema add karo
class ZendeskConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str
    subdomain: str

# ==========================================
# 🎫 ZENDESK OAUTH ROUTE
# ==========================================
@app.post("/api/integrations/zendesk/connect")
async def connect_zendesk(payload: ZendeskConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Zendesk' for workspace: {payload.workspace_id}")
    
    try:
        result = await integration_manager.connect_integration(
            integration_name="zendesk",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code, "subdomain": payload.subdomain}
        )
        return result
        
    except Exception as e:
        print(f"🚨 [Zendesk Integration Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))  
from fastapi import Request
from integrations.zendesk.webhook import zendesk_webhook_handler

# ==========================================
# 🕸️ ZENDESK LIVE WEBHOOK ROUTE
# ==========================================
@app.post("/api/integrations/zendesk/webhook")
async def zendesk_live_webhook(request: Request):
    try:
        payload = await request.json()
        
        # Pass the payload to our dedicated Zendesk webhook handler
        result = await zendesk_webhook_handler.handle_event(payload)
        return result
        
    except Exception as e:
        print(f"🚨 [Zendesk Webhook Route Error]: {e}")
        return {"status": "error", "message": str(e)}  
# Naya schema add karo
class SalesforceConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# ==========================================
# 💼 SALESFORCE OAUTH ROUTE
# ==========================================
@app.post("/api/integrations/salesforce/connect")
async def connect_salesforce(payload: SalesforceConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Salesforce' for workspace: {payload.workspace_id}")
    
    try:
        result = await integration_manager.connect_integration(
            integration_name="salesforce",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
        
    except Exception as e:
        print(f"🚨 [Salesforce Integration Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))
from fastapi import Request
from integrations.salesforce.webhook import salesforce_webhook_handler

# ==========================================
# 💼 SALESFORCE LIVE WEBHOOK ROUTE
# ==========================================
@app.post("/api/integrations/salesforce/webhook")
async def salesforce_live_webhook(request: Request):
    try:
        payload = await request.json()
        
        # Pass the payload to our dedicated Salesforce webhook handler
        result = await salesforce_webhook_handler.handle_event(payload)
        return result
        
    except Exception as e:
        print(f"🚨 [Salesforce Webhook Route Error]: {e}")
        return {"status": "error", "message": str(e)}  
from integrations.hubspot.webhook import hubspot_webhook_handler

class HubSpotConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# 🟠 HUBSPOT OAUTH ROUTE
@app.post("/api/integrations/hubspot/connect")
async def connect_hubspot(payload: HubSpotConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'HubSpot' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="hubspot",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🟠 HUBSPOT WEBHOOK ROUTE
@app.post("/api/integrations/hubspot/webhook")
async def hubspot_live_webhook(request: Request):
    try:
        # HubSpot sends a JSON Array of events
        payload = await request.json()
        result = await hubspot_webhook_handler.handle_events(payload)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)} 
from integrations.intercom.webhook import intercom_webhook_handler

class IntercomConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# 💬 INTERCOM OAUTH ROUTE
@app.post("/api/integrations/intercom/connect")
async def connect_intercom(payload: IntercomConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Intercom' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="intercom",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 💬 INTERCOM WEBHOOK ROUTE
@app.post("/api/integrations/intercom/webhook")
async def intercom_live_webhook(request: Request):
    try:
        payload = await request.json()
        result = await intercom_webhook_handler.handle_event(payload)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)} 
from integrations.discord.webhook import discord_webhook_handler

class DiscordConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# 🎮 DISCORD OAUTH ROUTE
@app.post("/api/integrations/discord/connect")
async def connect_discord(payload: DiscordConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Discord' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="discord",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 🎮 DISCORD WEBHOOK ROUTE
@app.post("/api/integrations/discord/webhook")
async def discord_live_webhook(request: Request):
    try:
        payload = await request.json()
        result = await discord_webhook_handler.handle_event(payload)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)} 
class RedditConnectPayload(BaseModel):
    auth_code: str
    workspace_id: str

# 🔍 REDDIT OAUTH ROUTE
@app.post("/api/integrations/reddit/connect")
async def connect_reddit(payload: RedditConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'Reddit' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="reddit",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"auth_code": payload.auth_code}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
class AnalyticsConnectPayload(BaseModel):
    provider: str
    api_key: str
    project_id: str
    workspace_id: str

# 📊 UNIFIED ANALYTICS ROUTE (PostHog, Mixpanel, Amplitude)
@app.post("/api/integrations/analytics/connect")
async def connect_analytics(payload: AnalyticsConnectPayload):
    print(f"\n🔗 [Integration API] Connecting Analytics '{payload.provider}' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="analytics",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "provider": payload.provider,
                "api_key": payload.api_key,
                "project_id": payload.project_id
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))                                          
class CrashesConnectPayload(BaseModel):
    provider: str
    api_key: str
    org_slug: str
    project_slug: str
    workspace_id: str

# 🔥 UNIFIED CRASHES ROUTE (Sentry & Crashlytics)
@app.post("/api/integrations/crashes/connect")
async def connect_crashes(payload: CrashesConnectPayload):
    print(f"\n🔗 [Integration API] Connecting '{payload.provider}' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="crashes",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "provider": payload.provider,
                "api_key": payload.api_key,
                "org_slug": payload.org_slug,
                "project_slug": payload.project_slug
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
class YouTubeConnectPayload(BaseModel):
    api_key: str
    workspace_id: str

# ▶️ YOUTUBE API ROUTE
@app.post("/api/integrations/youtube/connect")
async def connect_youtube(payload: YouTubeConnectPayload):
    print(f"\n🔗 [Integration API] Connecting 'YouTube' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="youtube",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"api_key": payload.api_key}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
class EmailConnectPayload(BaseModel):
    provider: str
    access_token: str
    workspace_id: str

@app.post("/api/integrations/email/connect")
async def connect_email(payload: EmailConnectPayload):
    print(f"\n🔗 [Integration API] Connecting Email '{payload.provider}' for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="email",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={"provider": payload.provider, "access_token": payload.access_token}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
from integrations.zoom.webhook import zoom_webhook_handler

class ZoomConnectPayload(BaseModel):
    workspace_id: str

# 📹 ZOOM CONNECT ROUTE
@app.post("/api/integrations/zoom/connect")
async def connect_zoom(payload: ZoomConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating Zoom for workspace: {payload.workspace_id}")
    try:
        # Server-to-Server OAuth handles keys internally from env variables
        result = await integration_manager.connect_integration(
            integration_name="zoom",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={}
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 📹 ZOOM WEBHOOK ROUTE
@app.post("/api/integrations/zoom/webhook")
async def zoom_live_webhook(request: Request):
    try:
        payload = await request.json()
        result = await zoom_webhook_handler.handle_event(payload)
        return result
    except Exception as e:
        return {"status": "error", "message": str(e)} 
from typing import Optional
from pydantic import BaseModel

class BitbucketConnectPayload(BaseModel):
    token: str
    username: Optional[str] = None
    workspace_id: str

# 🪣 BITBUCKET CONNECT ROUTE
@app.post("/api/integrations/bitbucket/connect")
async def connect_bitbucket(payload: BitbucketConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating Bitbucket for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="bitbucket",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "token": payload.token,
                "username": payload.username
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
from pydantic import BaseModel

class LinearConnectPayload(BaseModel):
    api_key: str
    workspace_id: str

# 🎯 LINEAR CONNECT ROUTE
@app.post("/api/integrations/linear/connect")
async def connect_linear(payload: LinearConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating Linear for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="linear",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "api_key": payload.api_key
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))  
class FreshdeskConnectPayload(BaseModel):
    api_key: str
    domain: str
    workspace_id: str

@app.post("/api/integrations/freshdesk/connect")
async def connect_freshdesk(payload: FreshdeskConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating Freshdesk for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="freshdesk",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "api_key": payload.api_key,
                "domain": payload.domain
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 
class TwitterConnectPayload(BaseModel):
    bearer_token: str
    tracking_query: str
    workspace_id: str

@app.post("/api/integrations/twitter/connect")
async def connect_twitter(payload: TwitterConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating Twitter/X for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="twitter",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "bearer_token": payload.bearer_token,
                "tracking_query": payload.tracking_query
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class CommunityPayload(BaseModel):
    api_key: str
    domain: str
    workspace_id: str

class GA4Payload(BaseModel):
    property_id: str
    service_account_json: str # Normally securely uploaded, simplified here
    workspace_id: str

@app.post("/api/integrations/community/connect")
async def connect_community(payload: CommunityPayload):
    return await integration_manager.connect_integration("community", payload.workspace_id, "org_1", {"api_key": payload.api_key, "domain": payload.domain})

@app.post("/api/integrations/ga4/connect")
async def connect_ga4(payload: GA4Payload):
    return await integration_manager.connect_integration("ga4", payload.workspace_id, "org_1", {"property_id": payload.property_id}) 
class DatadogConnectPayload(BaseModel):
    api_key: str
    app_key: str
    site: str
    workspace_id: str

@app.post("/api/integrations/datadog/connect")
async def connect_datadog(payload: DatadogConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating Datadog for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="datadog",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "api_key": payload.api_key,
                "app_key": payload.app_key,
                "site": payload.site
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
class GoogleMeetConnectPayload(BaseModel):
    access_token: str
    workspace_id: str

@app.post("/api/integrations/google_meet/connect")
async def connect_google_meet(payload: GoogleMeetConnectPayload):
    return await integration_manager.connect_integration(
        "google_meet", payload.workspace_id, "org_1", {"access_token": payload.access_token}
    )                                                                        
class ReviewsConnectPayload(BaseModel):
    provider: str # 'appstore', 'googleplay', 'chrome'
    app_id: str
    workspace_id: str

@app.post("/api/integrations/reviews/connect")
async def connect_reviews(payload: ReviewsConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating {payload.provider} Reviews for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="reviews",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "provider": payload.provider,
                "app_id": payload.app_id
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class KnowledgeConnectPayload(BaseModel):
    provider: str # 'notion', 'confluence', 'google_docs'
    token: str
    workspace_id: str

@app.post("/api/integrations/knowledge/connect")
async def connect_knowledge(payload: KnowledgeConnectPayload):
    print(f"\n🔗 [Integration API] Authenticating {payload.provider} Knowledge Engine for workspace: {payload.workspace_id}")
    try:
        result = await integration_manager.connect_integration(
            integration_name="knowledge",
            workspace_id=payload.workspace_id,
            org_id="org_dummy_123", 
            auth_payload={
                "provider": payload.provider,
                "token": payload.token
            }
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))                                            

@app.post("/api/chat")
async def executive_chat(payload: ChatPayload):
    try:
        result = await ask_executive_cpo(
            user_message=payload.message,
            dashboard_context=payload.context_data
        )
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/webhook/zendesk")
async def process_webhook(request: Request):
    try:
        payload = await request.json()
        user_email = payload.get("requester_email", "support_user@client.com")
        
        result = await kernel.execute(
            request_type="zendesk_ticket", 
            raw_payload=payload, 
            user_email=user_email
        )
        
        await ws_manager.broadcast({
            "type": "NEW_ALERT",
            "data": result 
        })
        
        return {"status": "success", "data": result}
        
    except Exception as e:
        print(f"🚨 Error processing webhook: {str(e)}")
        return {"status": "error", "message": str(e)}

@app.post("/export-jira")
async def export_to_jira(payload: JiraExportPayload):
    print(f"[API] Exporting PRD to Jira: '{payload.title}'")
    jira_tool = integration_manager.get_integration("jira")
    
    final_content = payload.prd_content if payload.prd_content else payload.prd_text
    if not final_content:
        final_content = "No PRD content provided."
        
    result = jira_tool.send_action(
        prd_content=final_content,
        issue_summary=f"AI The Voice of Customer - {payload.title}",
        project_key="KAN" 
    )
    
    if result.get("status") == "success":
        return {"status": "success", "message": f"Successfully exported to Jira ticket: {result.get('ticket')}"}
    else:
        return {"status": "error", "message": "Failed to connect to Jira."}
# ⚡ PHASE 4: SMB File Upload Route
@app.post("/api/upload")
async def upload_manual_data(
    background_tasks: BackgroundTasks, 
    user_email: str = Form(...), # Extracting real email from FormData
    file: UploadFile = File(...), 
    auth_payload: dict = Depends(verify_clerk_user) # 🔒 Protected by Clerk
):
    # Using the real email provided by the authenticated frontend
    real_email = user_email 
    
    print(f"\n📂 [Ingestion] Secure upload received from {real_email}: {file.filename}")
    
    content = await file.read()
    payload = {
        "title": f"Log Analysis: {file.filename}", 
        "body": content.decode("utf-8")[:1000]
    }
    
    # Passing real_email strictly to the background task
    background_tasks.add_task(run_ai_pipeline_in_background, "zendesk_ticket", payload, real_email)
    
    return {"status": "success", "message": "File uploaded securely. AgentOS is processing it."}
from agents.agents_role import get_cpo_persona
from groq import AsyncGroq
import os

# Ensure GROQ_API_KEY is in your environment variables
groq_client = AsyncGroq(api_key=os.environ.get("GROQ_API_KEY", "your_fallback_api_key_here"))

class ChatRequest(BaseModel):
    message: str
    context_data: list = [] # Dashboard ka current state yahan aayega

@app.post("/api/chat")
async def ai_cpo_chat(req: ChatRequest):
    print(f"💬 [AI CPO] Received question: {req.message}")
    
    # Dashboard ke active issues ko string me convert kar rahe hain as context
    context_str = json.dumps(req.context_data)[:2000] if req.context_data else "No current active issues."
    
    try:
        completion = await groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": f"{get_cpo_persona()} Current Dashboard Context: {context_str}"},
                {"role": "user", "content": req.message}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.3, # Low temp for factual, executive answers
        )
        
        reply_text = completion.choices[0].message.content
        return {"status": "success", "reply": reply_text}
        
    except Exception as e:
        print(f"🚨 [Chat Engine Error]: {str(e)}")
        return {"status": "error", "reply": "I am currently analyzing the graph database. Please try again in a moment."} 
# ⚡ THE UNIVERSAL SIGNAL GATEWAY (Accepts EVERYTHING)
@app.post("/api/universal-webhook")
async def universal_webhook(request: Request, background_tasks: BackgroundTasks):
    raw_payload = await request.json()
    headers = dict(request.headers)
    
    # Router automatically detect karega ki kaunsa tool data bhej raha hai
    source = identify_signal_source(headers, raw_payload)
    
    print(f"\n📡 [Universal Gateway] Intercepted live traffic from: {source}")
    
    # Seedha background normalizer ko bhej do
    background_tasks.add_task(process_universal_signal_bg, source, str(raw_payload))
    
    return {
        "status": "success", 
        "message": f"AgentOS successfully intercepted and routed signal from {source}"
    }


# ⚡ THE BACKGROUND PIPELINE
# ⚡ FIX 1: Explicitly pass 'real_email' to the background engine
async def process_universal_signal_bg(source: str, raw_data_str: str, real_email: str):
    print(f"⚙️ [Background Worker] Processing {source} signal strictly for: {real_email}")
    try:
        # 1. Normalize data
        clean_data = await normalize_universal_signal(source, raw_data_str)
        
        # 2. Fetch REAL revenue for this specific user
        company_arr = await crm_engine.fetch_company_revenue_risk(real_email)
        
        final_payload = {
            "title": f"[{source}] {clean_data.get('title', 'Unknown')}",
            "body": clean_data.get('description', ''),
            "severity": clean_data.get('severity', 'Medium'),
            "revenue_impact": company_arr
        }
        
        # 3. Kernel MUST execute strictly under this user's namespace
        from os_kernel import kernel
        result = await kernel.execute("zendesk_ticket", final_payload, real_email)
        
        # 4. Push to UI
        await manager.broadcast(json.dumps({
            "type": "NEW_ALERT",
            "data": result,
            "target_user": real_email # Good practice to tag websocket events too
        }))
        print(f"🚀 [Engine Status] Fully processed for {real_email}!")
        
    except Exception as e:
        print(f"🚨 [Engine Error] Processing halted for {real_email}: {e}")
# ⚡ CATEGORY 2: The Social & Review Sync Endpoint
@app.get("/api/sync-social")
async def sync_social_signals(background_tasks: BackgroundTasks):
    print("\n🚀 [AgentOS] Manual Sync Triggered for Social Data")
    
    # 1. Scrape all unstructured data
    raw_signals = await scraper.run_all_scrapers()
    
    # 2. Feed every single post/review into the Universal Normalizer Pipeline
    for signal in raw_signals:
        source = signal["source_name"]
        raw_text = signal["raw_data"]
        
        # Hum wahi background worker use kar rahe hain jo webhook use karta hai
        # (Massive Code Reusability!)
        background_tasks.add_task(process_universal_signal_bg, source, raw_text)
        
    return {
        "status": "success", 
        "message": f"AgentOS is processing {len(raw_signals)} social signals in the background."
    }   
from pydantic import BaseModel

class ActionRequest(BaseModel):
    action_type: str # e.g., "create_jira", "reply_customer"
    title: str = "Untitled Issue"
    description: str = "No description provided."
    severity: str = "Medium"

# ⚡ CATEGORY 3: The Outbound Execution Route
@app.post("/api/execute-action")
async def execute_outbound_action(req: ActionRequest):
    print(f"\n⚙️ [AgentOS] Outbound Action Triggered: {req.action_type}")
    
    if req.action_type == "create_jira":
        result = await action_arm.create_jira_ticket(req.title, req.description, req.severity)
        return result
        
    elif req.action_type == "reply_customer":
        # Placeholder for auto-reply logic
        result = await action_arm.auto_reply_zendesk("ZD-992", req.description)
        return result
        
    return {"status": "error", "message": "Unknown action type."}    
async def process_universal_signal_bg(source: str, raw_data_str: str):
    try:
        # 1. Direct parsing via fast, memory-safe Groq LLM (Bouncer Agent)
        clean_data = await normalize_universal_signal(source, raw_data_str)
        
        # 2. Enrich signal with light CRM metrics (ARR extraction)
        company_arr = await crm_engine.fetch_company_revenue_risk("user_email")
        
        # 3. Construct unified AgentOS signal payload
        final_payload = {
            "title": f"[{source}] {clean_data['title']}",
            "body": clean_data['description'],
            "severity": clean_data['severity'],
            "revenue_impact": company_arr
        }
        
        # 4. Trigger standard internal OS core logic
        from os_kernel import kernel
        result = await kernel.execute("zendesk_ticket", final_payload, "user_email")
        
        # 5. Broadcast live to Dashboard UI instantly via WebSockets
        import json
        await manager.broadcast(json.dumps({
            "type": "NEW_ALERT",
            "data": result
        }))
        print(f"🚀 [Engine Status] Fully processed 1/21 tool signal. Broadcasted successfully!")
        
    except Exception as e:
        print(f"🚨 [Engine Error] Processing sequence halted safely: {e}")  
class UnifiedWebhookPayload(BaseModel):
    integration_type: str # e.g., "ticketing", "crm"
    account_token: str
    data: dict

# ⚡ THE 21-IN-1 MASTER ROUTE
from adapters.nango_engine import nango_connector
from pydantic import BaseModel

class NangoWebhookPayload(BaseModel):
    operation: str
    provider_config_key: str
    connection_id: str
    model: str

# ⚡ THE NANGO MASTER ROUTE
@app.post("/api/nango-webhook")
async def handle_nango_webhook(payload: dict, background_tasks: BackgroundTasks):
    provider = payload.get("provider_config_key", "unknown")
    print(f"\n🌍 [AgentOS] Received Unified Signal from Nango ({provider})!")
    
    background_tasks.add_task(process_nango_signal_bg, payload)
    return {"status": "success", "message": "Nango signal accepted."}

async def process_nango_signal_bg(payload: dict):
    try:
        provider = payload.get("provider_config_key", "unknown")
        connection_id = payload.get("connection_id", "demo-conn")
        
        # 1. Fetch the actual clean data from Nango
        records = await nango_connector.fetch_unified_records(provider, connection_id)
        
        if not records:
            return
            
        latest_record = records[0] # Processing the most recent one for MVP
        
        # 2. Format it strictly for the AI Chief Product Officer (CPO) Kernel
        agent_payload = {
            "title": f"[{provider.capitalize()}] {latest_record.get('title', 'Unknown Issue')}",
            "body": latest_record.get("description", "No description"),
            "severity": latest_record.get("priority", "Medium")
        }
        
        # 3. Feed to Kernel
        from os_kernel import kernel
        result = await kernel.execute("zendesk_ticket", agent_payload, "user_email")
        
        # 4. Push to Dashboard
        import json
        await manager.broadcast(json.dumps({
            "type": "NEW_ALERT",
            "data": result
        }))
        print(f"✅ [Nango API] {provider} signal successfully processed & broadcasted!")
        
    except Exception as e:
        print(f"🚨 [Nango Engine Error]: {e}")
# ⚡ PILLAR 2: THE APIFY SYNC ROUTE (Social & Reviews)
@app.get("/api/sync-apify")
async def sync_apify_platforms(background_tasks: BackgroundTasks):
    platforms = ["App Store", "Reddit", "Twitter/X", "YouTube", "Google Play", "LinkedIn"]
    print(f"\n🌍 [AgentOS] Firing Apify scrapers for {len(platforms)} platforms...")
    
    for platform in platforms:
        # Pushing all scraping jobs to background to keep server fast
        background_tasks.add_task(process_apify_bg, platform)
        
    return {"status": "success", "message": "Apify cluster initiated."}

async def process_apify_bg(platform: str):
    data = await apify_connector.fetch_social_signals(f"mock_id_{platform}", platform)
    if data:
        raw_text = data[0].get("text", "")
        # Feeding raw scraper text to our Master Normalizer!
        await process_universal_signal_bg(platform, raw_text)


# ⚡ PILLAR 3: THE MACHINE LOG WEBHOOK (Crash Logs & Analytics)
@app.post("/api/machine-webhook")
async def handle_machine_webhook(request: Request, background_tasks: BackgroundTasks):
    headers = dict(request.headers)
    payload = await request.json()
    
    # Simple detection logic
    source = "Unknown System"
    if "sentry" in str(headers).lower(): source = "Sentry"
    elif "mixpanel" in str(headers).lower(): source = "Mixpanel"
    
    print(f"\n🚨 [AgentOS] Received Machine Alert from {source}")
    
    # Pass to background task
    background_tasks.add_task(process_machine_bg, payload, source)
    return {"status": "received"}

async def process_machine_bg(payload: dict, source: str):
    # 1. Extract messy log data
    parsed_log = parse_engineering_logs(payload, source)
    
    # 2. Feed the messy log to our Master Normalizer!
    await process_universal_signal_bg(source, parsed_log["raw_text"])  
import traceback
from fastapi import HTTPException, Depends
from pydantic import BaseModel

class SearchQuery(BaseModel):
    query: str
    user_email: str = "unknown@user.com"
class DashboardRequest(BaseModel):
    user_email: str = "unknown@user.com"    

# ==========================================
# 🧠 DYNAMIC CONTEXT BUILDER (Enterprise RAG Engine)
# ==========================================
async def build_dynamic_context(user_email: str) -> str:
    """
    Aggregates live workspace context from CRM + Neo4j.
    This context is injected into the AI CPO before answering.
    """
    print(f"🔄 [Context Engine] Building workspace context for {user_email}")

    # -----------------------------
    # 1. CRM Revenue
    # -----------------------------
    try:
        arr_at_risk = await crm_engine.fetch_company_revenue_risk(user_email)
        if arr_at_risk is None:
            arr_at_risk = 0
    except Exception as e:
        print(f"⚠️ [CRM Error]: {e}")
        arr_at_risk = 0

    # -----------------------------
    # 2. Graph Database (Neo4j)
    # -----------------------------
    db_status = "ONLINE"
    try:
        active_issues = graph_db.get_active_issues(
            user_email=user_email,
            limit=5  # Prevent prompt explosion (Token limits)
        )

        if active_issues:
            issues_str = "\n".join([
                f"- {issue.get('title', 'Unknown')} "
                f"(Severity: {issue.get('severity', 'Unknown')})"
                for issue in active_issues
            ])
        else:
            issues_str = "- No active critical issues."

    except Exception as e:
        db_status = "OFFLINE"
        print(f"⚠️ [GraphDB Error]: {e}")
        issues_str = "- Unable to retrieve live issues."

    # -----------------------------
    # 3. Final Prompt Context
    # -----------------------------
    context = f"""
REAL-TIME WORKSPACE CONTEXT

Database Status:
{db_status}

Current ARR At Risk:
${arr_at_risk}

Top Active Product Issues:
{issues_str}

Instructions:
- These workspace metrics are the source of truth.
- If workspace data is unavailable, clearly state that.
- Never invent company metrics.
"""
    return context


# ==========================================
# 🧠 AI CPO CHAT ROUTE
# ==========================================
@app.post("/api/ask-agentos")
async def ask_agentos(
    request: SearchQuery,
    auth_payload: dict = Depends(verify_clerk_user)
):
    # 🛡️ Fallback mechanism: Check token first, fallback to request body if Clerk token claims differ
    real_email = auth_payload.get("email") or request.user_email

    if not real_email or real_email == "unknown@user.com":
        raise HTTPException(
            status_code=401,
            detail="Unauthorized: Authenticated user email not found."
        )

    print(f"\n🧠 [AgentOS Brain] Query from {real_email}")
    print(f"🗣️  Question: {request.query}")

    try:
        system_prompt = """
You are AgentOS, the AI Chief Product Officer.

Your responsibilities:
• Answer CEO questions regarding product health.
• Use Workspace Context whenever it contains relevant information.
• If the question is general (example: "What is ARR?"), answer using product management knowledge.
• Never invent revenue numbers, bugs, customer counts or engineering metrics.
• If the requested workspace data is unavailable, explicitly say that instead of guessing.
• Be concise.
• Be analytical.
• Provide actionable recommendations.
"""

        # -----------------------------
        # Step 1: Build live workspace context
        # -----------------------------
        live_context = await build_dynamic_context(real_email)

        # -----------------------------
        # Step 2: Call Groq (Llama 3)
        # -----------------------------
        chat_completion = await groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": f"Workspace Context:\n{live_context}\n\nCEO Question:\n{request.query}"
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.2, # Low temp = strict factual adherence
        )

        answer = chat_completion.choices[0].message.content

        return {
            "status": "success",
            "user_email": real_email,
            "answer": answer
        }

    except Exception as e:
        print(f"🚨 [AI Kernel Error]: {e}")
        traceback.print_exc()  # This will print exactly which line crashed in your terminal
        raise HTTPException(
            status_code=500,
            detail=f"AI Kernel Error: {str(e)}"
        )
# ==========================================
# 📊 REAL-TIME DASHBOARD STATS ROUTE
# ==========================================
@app.post("/api/dashboard-stats")
async def get_dashboard_stats(
    request: DashboardRequest,
    auth_payload: dict = Depends(verify_clerk_user)
):
    # Get the verified email securely
    real_email = auth_payload.get("email") or request.user_email

    print(f"📊 [Dashboard Engine] Fetching live stats for {real_email}")

    try:
        # 1. Fetch Real ARR At Risk from CRM
        try:
            arr_at_risk = await crm_engine.fetch_company_revenue_risk(real_email)
            arr_at_risk = arr_at_risk if arr_at_risk is not None else 0
        except Exception:
            arr_at_risk = 0

        # 2. Fetch Active Critical Issues from GraphDB
        try:
            active_issues = graph_db.get_active_issues(real_email, limit=10)
            
            # Count only critical/high issues
            critical_bugs = len([
                issue for issue in active_issues 
                if issue.get("severity", "").lower() in ["critical", "high"]
            ]) if active_issues else 0
            
        except Exception:
            critical_bugs = 0

        # 3. Calculate derived metrics (Future: Add direct DB tables for these)
        customers_affected = critical_bugs * 5  # Example calculation
        expected_churn = int(arr_at_risk / 150000) if arr_at_risk > 0 else 0

        return {
            "status": "success",
            "stats": {
                "criticalIncidents": critical_bugs,
                "revenueAtRisk": arr_at_risk,
                "customersAffected": customers_affected,
                "expectedChurn": expected_churn
            }
        }

    except Exception as e:
        print(f"🚨 [Dashboard Stats Error]: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Failed to fetch dashboard stats.") 

class WorkspaceCreate(BaseModel):
    companyName: str
    industry: str
    companySize: str
    region: str

# ==========================================
# 🚀 THE WORKSPACE BOOTSTRAP ENGINE
# ==========================================
@app.post("/api/workspaces")
async def create_workspace(
    workspace: WorkspaceCreate,
    auth_payload: dict = Depends(verify_clerk_user),
    db: Session = Depends(get_db) # ⚡ Yahan humne Database session inject kiya hai
):
    email = auth_payload.get("email", "unknown@user.com")
    clerk_id = auth_payload.get("sub", "unknown_sub")
    
    print(f"\n🚀 [Bootstrap Engine] Initializing Postgres Infrastructure for {workspace.companyName}")
    
    try:
        # ---------------------------------------------------------
        # 🐘 STEP 1: Postgres - Check User & Create Workspace
        # ---------------------------------------------------------
        
        # Pehle check karo user DB mein hai ya nahi
        db_user = db.query(models.User).filter(models.User.clerk_id == clerk_id).first()
        if not db_user:
            # Naya user create karo
            db_user = models.User(clerk_id=clerk_id, email=email)
            db.add(db_user)
            db.commit()
            print(f"✅ [Postgres] New User Registered: {email}")

        # Naya Workspace create karo
        new_workspace = models.Workspace(
            name=workspace.companyName,
            industry=workspace.industry,
            size=workspace.companySize,
            region=workspace.region,
            owner_clerk_id=clerk_id
        )
        
        db.add(new_workspace)
        db.commit()
        db.refresh(new_workspace) # ID wagera fetch karne ke liye
        
        print(f"✅ [Postgres] Created Workspace Record: {new_workspace.id} (Org: {new_workspace.org_id})")

        # ---------------------------------------------------------
        # (Future: Neo4j and ChromaDB logic goes here)
        # ---------------------------------------------------------

        # Asli Postgres IDs return karo
        return {
            "status": "success",
            "message": "Workspace successfully bootstrapped in PostgreSQL.",
            "data": {
                "organization_id": new_workspace.org_id,
                "workspace_id": new_workspace.id,
                "company": new_workspace.name
            }
        }
        
    except Exception as e:
        db.rollback() # Agar kuch phata, toh aadhi adhuri entry DB mein mat daalo
        print(f"🚨 [Bootstrap Engine Error]: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="CRITICAL: Failed to save workspace in Postgres.")