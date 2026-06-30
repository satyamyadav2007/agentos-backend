# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from orchestrator import run_orchestrator
from database.graph_manager import graph_db
from github import Github
from pydantic import BaseModel

app = FastAPI(title="AI Chief Product Officer API", version="1.0")

# CORS Setup - Ye Next.js (port 3000) ko API access karne deta hai
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js ka URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
class GithubPayload(BaseModel):
    repo_name: str
    token: str

class FeedbackPayload(BaseModel):
    source: str
    raw_text: str
    user_email: str

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
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/causal-summary")
async def get_causal_analytics():
    print("[API] Fetching Causal Summary...")
    try:
        summary_data = await graph_db.get_causal_summary()
        
        if not summary_data:
            raise Exception("No data found")
            
        return {"status": "success", "data": summary_data}
    except Exception as e:
        print(f"[Warning] Neo4j offline or empty. Returning Mock Data for UI. Error: {e}")
        # MOCK DATA: Taaki frontend ka UI hamesha kaam kare
        mock_data = [
            {
                "FailedRelease": "v2.8", 
                "RootCauseBug": "SSO OAuth Timeout (Mocked Data)", 
                "ImpactedCustomers": 3, 
                "TotalARRDamaged": 1150000
            },
            {
                "FailedRelease": "v2.7", 
                "RootCauseBug": "Billing Page Crash (Mocked Data)", 
                "ImpactedCustomers": 8, 
                "TotalARRDamaged": 420000
            }
        ]
        return {"status": "success", "data": mock_data}   
@app.post("/process-github")
async def process_github_issues(payload: GithubPayload):
    print(f"[GitHub] Fetching issues for {payload.repo_name}...")
    try:
        g = Github(payload.token)
        repo = g.get_repo(payload.repo_name)
        
        # 1. Safely fetch paginated list
        open_issues = repo.get_issues(state='open')
        
        # 2. 🚨 NAYA CHECK: Agar ek bhi issue nahi hai, toh gracefully return karo
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
        
        processed_results = []
        total_risk = 0
        
        # 4. Process only the valid issues
        for issue in issues_to_process:
            raw_text = f"{issue.title} - {issue.body}" if issue.body else issue.title
            user_email = f"{issue.user.login}@github-user.com"
            
            result = await run_orchestrator(
                text=raw_text, 
                source="GitHub API",
                user_email=user_email
            )
            
            if result and result.get("revenue_impact"):
                total_risk += result["revenue_impact"].get("revenue_at_risk", 0)
            
            processed_results.append({
                "originalText": issue.title,
                "email": user_email,
                "analysis": result["analysis"],
                "revenue": result["revenue_impact"],
                "prd_draft": result["prd_draft"]
            })
                
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