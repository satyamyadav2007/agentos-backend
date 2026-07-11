from typing import Dict, Any
from .models.devsecops import GitLabPipelineModel, GitLabMergeRequestModel

class GitLabNormalizer:
    
    @staticmethod
    def normalize_pipeline(pipeline: GitLabPipelineModel) -> Dict[str, Any]:
        """Converts a GitLab CI/CD Pipeline status into an AgentOS UniversalEvent."""
        
        # A failed production pipeline triggers an immediate P0 Event
        severity = "Critical" if pipeline.is_critical_failure else "Low" if pipeline.status == "success" else "Medium"

        return {
            "source": "gitlab",
            "entity_type": "ci_pipeline",
            "repository": f"Project_{pipeline.project_id}", 
            "title": f"Pipeline {pipeline.status.upper()} on branch '{pipeline.ref}'",
            "description": f"CI/CD Pipeline {pipeline.id} finished with status: {pipeline.status}. View here: {pipeline.web_url}",
            "author": "GitLab CI/CD",
            "severity": severity,
            "timestamp": pipeline.updated_at.isoformat(),
            "metadata": {
                "pipeline_id": pipeline.id,
                "status": pipeline.status,
                "branch": pipeline.ref
            },
            # Module 20: Neo4j will connect this to Jira Tickets & Sentry Crashes!
            "linked_entities": [] 
        }