# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from github import Github
import traceback

# Custom Agents & Managers
from orchestrator import run_orchestrator
from agents.jira_agent import create_jira_ticket
from agents.chat_agent import ask_executive_cpo
from database.graph_manager import graph_db
from integrations.manager import integration_manager
from typing import Optional
# main.py ke top par yeh import add karo
from agents.support_agent import translate_customer_ticket
from orchestrator import process_single_issue
app = FastAPI(title="AI Chief Product Officer API", version="1.0")

 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get("/health")
def system_health_check():
    return {
        "status": "Operational",
        "platform": "AgentOS AI CPO",
        "modules": ["Neo4j", "ChromaDB", "Groq_LLM", "Orchestrator"],
        "readiness": "100%"
    }

# Yeh naya route define karo file ke neeche
class SupportTicketPayload(BaseModel):
    ticket_text: str
    client_email: str

@app.post("/process-support")
async def process_support_ticket(payload: SupportTicketPayload):
    print(f"[API] Received support ticket from {payload.client_email}")
    
    # 1. Translate Customer English -> Technical Bug
    technical_issue = await translate_customer_ticket(payload.ticket_text)
    
    # 2. Bhej do hamare master Orchestrator ko (jo Vector DB aur PRD handle karta hai)
    # Orchestrator khud check karega ki kya ye ticket kisi existing GitHub bug se match karta hai!
    final_result = await process_single_issue(
        issue_data=technical_issue,
        user_email=payload.client_email
    )
    
    return {"status": "success", "data": final_result}

# Jab koi high-risk bug aaye:
slack_tool = integration_manager.get_integration("slack")
slack_tool.send_action("🚨 *AgentOS Alert:* Found a new critical bug risking $1,000 ARR. PRD drafted and sent to Jira (KAN-4).")





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

# --- Routes ---

@app.get("/")
async def root():
    return {"message": "Welcome to AI Chief Product Officer API! The engine is running."}

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
        # Seedha graph database se data fetch karo
        real_insights = graph_db.get_causal_insights()
        
        return {
            "status": "success",
            "data": real_insights
        }
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))  

@app.post("/process-github")
async def process_github_issues(payload: GithubPayload):
    print("[API] Processing GitHub Issues...")
    try:
        repo_name = payload.repo_name
        token = payload.token
        
        g = Github(token)
        repo = g.get_repo(repo_name)
        
        # 1. Safely fetch paginated list
        open_issues = repo.get_issues(state='open')
        
        # 2. Agar ek bhi issue nahi hai, toh gracefully return karo
        if open_issues.totalCount == 0:
            print("[GitHub] No open issues found in this repository.")
            return {
                "status": "success", 
                "data": {
                    "issues": [],
                    "total_risk": 0
                },
                "message": "No open issues found. Please create a dummy issue in GitHub!"
            }
        
        # 3. Safely extract top 5 real issues (excluding Pull Requests)
        issues_to_process = []
        for issue in open_issues:
            if not issue.pull_request:
                issues_to_process.append(issue)
            if len(issues_to_process) >= 5:
                break
                
        # 🚨 THE FIX: Convert GitHub objects to dictionaries for the new Orchestrator
        formatted_issues = []
        for issue in issues_to_process:
            formatted_issues.append({
                "id": issue.number,
                "title": issue.title,
                "body": issue.body or "",
                "user_login": issue.user.login
            })
        
        # 4. Call the new Parallel Orchestrator just ONCE for the whole batch
        processed_results = []
        total_risk = 0
        
        if formatted_issues:
            default_email = f"{formatted_issues[0]['user_login']}@github-user.com"
            # Naya orchestrator puri list leta hai
            orchestrator_result = await run_orchestrator(github_issues=formatted_issues, user_email=default_email)
            
            processed_results = orchestrator_result["issues"]
            total_risk = orchestrator_result["total_risk"]
            
        # 5. Push data to Neo4j Knowledge Graph
        if processed_results:
            print("[System] Pushing data to Neo4j Knowledge Graph...")
            graph_db.ingest_github_data(processed_results)
            
            # ==========================================
            # 🚨 THE SLACK ALERT STEP 🚨
            # ==========================================
            slack_msg = f"🚨 *AgentOS Update:* Processed {len(processed_results)} open issues from GitHub.\n💰 *Total Revenue at Risk:* ${total_risk}\n🧠 Knowledge Graph updated successfully. AI CPO is ready for queries."
            
            slack_tool = integration_manager.get_integration("slack")
            slack_tool.send_action(slack_msg)

        return {
            "status": "success",
            "data": {
                "issues": processed_results,
                "total_risk": total_risk
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
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




# Yeh sab kuch accept kar lega, aur kuch missing hua toh default value use karega
class JiraExportPayload(BaseModel):
    title: Optional[str] = "AI Generated Jira Task"
    prd_content: Optional[str] = "Auto-generated PRD details will appear here."
    # Purane version ke phantom fields ko handle karne ke liye (taki crash na ho)
    domain: Optional[str] = None
    email: Optional[str] = None
    token: Optional[str] = None
    project_key: Optional[str] = "KAN"
    prd_text: Optional[str] = None

@app.post("/export-jira")
async def export_to_jira(payload: JiraExportPayload):
    print(f"[API] Exporting PRD to Jira: '{payload.title}'")
    
    # Switchboard se Jira tool nikalo
    jira_tool = integration_manager.get_integration("jira")
    
    # Dono variables me se jo bhi frontend ne bheja ho, usko pick karo
    final_content = payload.prd_content if payload.prd_content else payload.prd_text
    if not final_content:
        final_content = "No PRD content provided."
        
    # Action send karo
   # main.py ke andar
    result = jira_tool.send_action(
        prd_content=final_content,
        issue_summary=f"AI The Voice of Customer - {payload.title}",
        project_key="KAN" # e.g., "KAN" ya "DEV"
    )
    
    if result.get("status") == "success":
        return {"status": "success", "message": f"Successfully exported to Jira ticket: {result.get('ticket')}"}
    else:
        return {"status": "error", "message": "Failed to connect to Jira."}     