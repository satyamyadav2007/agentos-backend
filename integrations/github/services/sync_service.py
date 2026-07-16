from typing import Dict, Any, List
from sqlalchemy.orm import Session
from database.models import UniversalEventRecord
from integrations.github.discovery import GitHubDiscovery
from integrations.github.extractors.issues import GitHubIssuesExtractor
from integrations.github.normalizer import GitHubNormalizer
from integrations.github.extractors.commits import GitHubCommitExtractor
from integrations.github.extractors.actions import GitHubActionsExtractor
from integrations.github.extractors.releases import GitHubReleasesExtractor
from integrations.github.extractors.discussions import GitHubDiscussionsExtractor
# Dhyan rakhna ki GitHubPRExtractor bhi import ho (agar tumhare code me nahi hai toh)

class GitHubSyncService:
    def __init__(self, client):
        self.client = client
        self.discovery = GitHubDiscovery(client)
        self.issues_extractor = GitHubIssuesExtractor(client)
        self.pr_extractor = GitHubPRExtractor(client) # Async version
        self.commit_extractor = GitHubCommitExtractor(client)
        self.actions_extractor = GitHubActionsExtractor(client)
        self.releases_extractor = GitHubReleasesExtractor(client)
        self.discussions_extractor = GitHubDiscussionsExtractor(client)
        
    async def run_full_sync(self, installation_id: str, workspace_id: str, db: Session):
        print("\n🚀 [GitHub Sync Service] Starting Full Intelligence Extraction...")
        repos = await self.discovery.fetch_authorized_repos(installation_id)
        
        db_records_to_insert = []
        all_universal_events = [] # ⚡ FIX 1: Array initialized here
        
        for repo in repos:
            repo_name = repo["full_name"]
            
            # 1. Fire all async extractors concurrently for maximum speed
            import asyncio
            issues, prs, commits, actions, releases, discussions = await asyncio.gather(
                self.issues_extractor.fetch_repository_issues(repo_name),
                self.pr_extractor.fetch_pull_requests(repo_name),
                self.commit_extractor.fetch_recent_commits(repo_name, limit=20),
                self.actions_extractor.fetch_recent_workflow_runs(repo_name, limit=10),
                self.releases_extractor.fetch_recent_releases(repo_name, limit=5),
                self.discussions_extractor.fetch_recent_discussions(repo_name, limit=10) # ⚡ GraphQL Concurrent Execution
            )
            
            # 2. Normalize Everything
            for issue in issues:
                norm = GitHubNormalizer.normalize_issue(issue.model_dump(), repo_name)
                all_universal_events.append(norm) # ⚡ FIX 2: Append to array for Neo4j
                db_records_to_insert.append(self._build_db_record(norm, workspace_id))
                
            for pr in prs:
                norm = GitHubNormalizer.normalize_pr(pr.model_dump(), repo_name)
                all_universal_events.append(norm) # ⚡ FIX 2: Append to array for Neo4j
                db_records_to_insert.append(self._build_db_record(norm, workspace_id))
                
            for commit in commits:
                norm = GitHubNormalizer.normalize_commit(commit.model_dump(), repo_name)
                all_universal_events.append(norm) # ⚡ FIX 2: Append to array for Neo4j
                db_records_to_insert.append(self._build_db_record(norm, workspace_id))
                
            for action in actions:
                norm = GitHubNormalizer.normalize_action(action, repo_name)
                all_universal_events.append(norm) # ⚡ FIX 2: Append to array for Neo4j
                db_records_to_insert.append(self._build_db_record(norm, workspace_id))

            for release in releases:
                norm = GitHubNormalizer.normalize_release(release.model_dump(), repo_name)
                all_universal_events.append(norm)
                db_records_to_insert.append(self._build_db_record(norm, workspace_id)) 
                
            for discussion in discussions:
                norm = GitHubNormalizer.normalize_discussion(discussion, repo_name)
                all_universal_events.append(norm)
                db_records_to_insert.append(self._build_db_record(norm, workspace_id))       

        # 3. Bulk Insert to Postgres
        if db_records_to_insert:
            db.bulk_save_objects(db_records_to_insert)
            db.commit()
            print(f"💾 [Postgres] Saved {len(db_records_to_insert)} diverse intelligence records!")

        # 4. Build Knowledge Graph in Neo4j (Sprint 3)
        if all_universal_events:
            from database.graph_manager import graph_db
            await graph_db.build_knowledge_graph(workspace_id, all_universal_events)
            
        print(f"🧠 [AgentOS Brain] Normalized {len(all_universal_events)} total events from GitHub!")
        return all_universal_events # ⚡ FIX 3: Returning the array

    def _build_db_record(self, normalized_data: dict, workspace_id: str):
        # Helper function to map dict to your SQLAlchemy UniversalEventRecord
        from database.models import UniversalEventRecord
        return UniversalEventRecord(
            workspace_id=workspace_id,
            source=normalized_data.get("source"),
            entity_type=normalized_data.get("entity_type"),
            repository=normalized_data.get("repository"),
            title=normalized_data.get("title"),
            severity=normalized_data.get("severity"),
            author=normalized_data.get("author"),
            metadata_json=normalized_data.get("metadata_json")
        )