import pytest
from integrations.github.normalizer import GitHubNormalizer

def test_normalize_issue_to_universal_event():
    # 1. Arrange: Sample Issue Dict (what comes out of Pydantic model_dump)
    raw_issue = {
        "id": 555,
        "number": 10,
        "title": "Payment gateway timeout",
        "body": "Stripe API taking too long.",
        "user": {"login": "satyam"},
        "labels": [{"name": "critical"}, {"name": "backend"}],
        "state": "open",
        "created_at": "2026-07-08T10:00:00Z"
    }
    
    # 2. Act
    universal_event = GitHubNormalizer.normalize_issue(raw_issue, "agentos/core")
    
    # 3. Assert
    assert universal_event["source"] == "github"
    assert universal_event["entity_type"] == "issue"
    assert universal_event["repository"] == "agentos/core"
    assert universal_event["title"] == "Payment gateway timeout"
    
    # Check AI severity logic (Should be High because of 'critical' label)
    assert universal_event["severity"] == "High"
    
    # Check Metadata
    assert universal_event["metadata"]["number"] == 10
    assert "critical" in universal_event["metadata"]["labels"]