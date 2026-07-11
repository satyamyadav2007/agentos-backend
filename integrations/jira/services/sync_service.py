from typing import Dict, Any, List
from integrations.jira.discovery import JiraDiscovery
from integrations.jira.extractors.issues import JiraIssuesExtractor
from integrations.jira.normalizer import JiraNormalizer

class JiraSyncService:
    """Orchestrates the entire data pipeline for Jira."""
    
    def __init__(self, client):
        self.client = client
        self.discovery = JiraDiscovery(client)
        self.issues_extractor = JiraIssuesExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Jira Sync Service] Starting Full Workspace Sync...")
        
        # 1. Discover Projects
        projects = await self.discovery.fetch_projects()
        
        all_normalized_events = []
        
        # 2. Extract & Normalize per Project
        for project in projects:
            project_key = project["key"]
            
            raw_issues = await self.issues_extractor.fetch_project_issues(project_key)
            
            for issue in raw_issues:
                normalized_event = JiraNormalizer.normalize_issue(issue)
                all_normalized_events.append(normalized_event)
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_normalized_events)} total events from Jira!")
        return all_normalized_events