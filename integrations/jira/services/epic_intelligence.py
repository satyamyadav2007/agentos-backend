from typing import Dict, Any, List

class JiraEpicIntelligence:
    """
    Module 6: Epic Intelligence Service.
    Analyzes Epics to calculate progress, detect blockers, and estimate revenue opportunity.
    """

    @staticmethod
    def analyze_epics(epics: List[Dict[str, Any]], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Processes normalized Epics and their associated issues to generate executive insights.
        """
        print("🏔️ [AgentOS AI] Generating Epic Intelligence...")
        
        epic_insights = []
        
        for epic in epics:
            epic_id = epic.get("id")
            title = epic.get("title", "Untitled Epic")
            
            # 1. Find child issues linked to this Epic
            # Matches issue parent_id or epic_id with the current Epic
            child_issues = [
                i for i in issues 
                if i.get("metadata", {}).get("epic_id") == epic_id 
                or i.get("metadata", {}).get("parent_id") == epic_id
            ]
            
            # 2. Calculate Progress (%)
            total_issues = len(child_issues)
            done_issues = len([
                i for i in child_issues 
                if i.get("metadata", {}).get("status", "").lower() in ["done", "closed", "resolved"]
            ])
            
            progress = 0
            if total_issues > 0:
                progress = int((done_issues / total_issues) * 100)
            
            # 3. Detect Blockers within the Epic
            blocked_issues = [
                i for i in child_issues 
                if "block" in i.get("metadata", {}).get("status", "").lower() 
                or "[blocked]" in i.get("title", "").lower()
            ]
            blocker_summary = "None"
            if blocked_issues:
                blocker_summary = f"{len(blocked_issues)} tasks blocked (e.g., {blocked_issues[0].get('title')})"
            
            # 4. Revenue Opportunity Estimation (AI Heuristics)
            # Scans the summary and description fetched from the extractor
            text = (title + " " + epic.get("description", "")).lower()
            revenue_opp = "$0"
            
            if any(k in text for k in ["pay", "checkout", "billing", "revenue", "stripe"]):
                revenue_opp = "$1.2M (High Impact)"
            elif any(k in text for k in ["auth", "security", "core", "infrastructure"]):
                revenue_opp = "$500K (Risk Mitigation)"
            elif epic.get("severity") in ["High", "Critical"]:
                revenue_opp = "$800K (Critical Path)"
            else:
                revenue_opp = "$100K (Standard Feature)"
                
            # 5. Executive AI Summary
            ai_summary = f"Epic '{title}' is currently at {progress}% completion. "
            if blocked_issues:
                ai_summary += f"It is facing delays due to {blocker_summary}."
            else:
                ai_summary += "Development is proceeding smoothly with no active blockers."
                
            epic_insights.append({
                "epic_id": epic_id,
                "title": title,
                "progress": f"{progress}%",
                "blocked_status": blocker_summary,
                "revenue_opportunity": revenue_opp,
                "executive_summary": ai_summary,
                "assignee": epic.get("author", "Unassigned")
            })
            
        return epic_insights