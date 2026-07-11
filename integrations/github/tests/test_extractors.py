import pytest
from unittest.mock import AsyncMock, MagicMock
from integrations.github.extractors.issues import GitHubIssuesExtractor
from integrations.github.models.issue import GitHubIssueModel

@pytest.mark.asyncio
async def test_fetch_repository_issues():
    # 1. Arrange: Create a Mock Client
    mock_client = AsyncMock()
    mock_client.get.return_value = [
        {
            "id": 123,
            "number": 42,
            "title": "Bug in production",
            "state": "open",
            "body": "System crashes on login.",
            "user": {"login": "satyam", "id": 1, "type": "User"},
            "labels": [{"name": "bug"}],
            "created_at": "2026-07-08T10:00:00Z",
            "updated_at": "2026-07-08T11:00:00Z"
        },
        {
            "id": 124,
            "number": 43,
            "title": "Add dark mode",
            "state": "closed",
            "user": {"login": "dev1", "id": 2, "type": "User"},
            "created_at": "2026-07-08T12:00:00Z",
            "updated_at": "2026-07-08T12:00:00Z",
            "pull_request": {"url": "..."} # This is a PR, should be filtered out
        }
    ]
    
    extractor = GitHubIssuesExtractor(client=mock_client)
    
    # 2. Act
    issues = await extractor.fetch_repository_issues("agentos/backend")
    
    # 3. Assert
    assert len(issues) == 1  # Should only extract 1 issue (the 2nd one is a PR)
    assert isinstance(issues[0], GitHubIssueModel)
    assert issues[0].number == 42
    assert issues[0].title == "Bug in production"