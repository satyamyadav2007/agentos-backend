from typing import Dict, Any, List

# Importing the new massive extractor suite!
from integrations.jira.extractors.projects import JiraProjectsExtractor
from integrations.jira.extractors.boards import JiraBoardsExtractor
from integrations.jira.extractors.issues import JiraIssuesExtractor
from integrations.jira.extractors.epics import JiraEpicsExtractor
from integrations.jira.extractors.sprints import JiraSprintExtractor
from integrations.jira.extractors.users import JiraUsersExtractor
from integrations.jira.normalizer import JiraNormalizer

class JiraSyncService:
    """Orchestrates the entire data pipeline for Jira (Enterprise Version)."""
    
    def __init__(self, client):
        self.client = client
        self.projects_ext = JiraProjectsExtractor(client)
        self.boards_ext = JiraBoardsExtractor(client)
        self.issues_ext = JiraIssuesExtractor(client)
        self.epics_ext = JiraEpicsExtractor(client)
        self.sprints_ext = JiraSprintExtractor(client)
        self.users_ext = JiraUsersExtractor(client)
        
    async def run_full_sync(self) -> List[Dict[str, Any]]:
        print("\n🚀 [Jira Sync Service] Starting Full Workspace Sync...")
        all_normalized_events = []
        
        # 1. Fetch Users for AI Capacity Planning
        await self.users_ext.fetch_all_users()
        
        # 2. Discover Projects (Replaced JiraDiscovery with JiraProjectsExtractor)
        projects = await self.projects_ext.fetch_projects()
        
        # 3. Extract & Normalize Everything per Project
        for project in projects:
            project_key = project["key"]
            print(f"\n⚙️ Scanning Project: {project_key}")
            
            # Fetch Issues
            raw_issues = await self.issues_ext.fetch_project_issues(project_key)
            for issue in raw_issues:
                all_normalized_events.append(JiraNormalizer.normalize_issue(issue))
                
            # Fetch Epics
            raw_epics = await self.epics_ext.fetch_project_epics(project_key)
            for epic in raw_epics:
                all_normalized_events.append(JiraNormalizer.normalize_epic(epic, project_key))
                
            # Fetch Sprints via Boards
            boards = await self.boards_ext.fetch_boards(project_key)
            for board in boards:
                board_id = board["id"]
                raw_sprints = await self.sprints_ext.fetch_active_sprints(board_id)
                for sprint in raw_sprints:
                    all_normalized_events.append(JiraNormalizer.normalize_sprint(sprint, project_key))
                
        print(f"🧠 [AgentOS Brain] Normalized {len(all_normalized_events)} total events (Issues, Epics, Sprints) from Jira!")
        return all_normalized_events