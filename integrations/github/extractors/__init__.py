"""
GitHub Extractors

Provides extractors for GitHub resources such as
issues, pull requests, commits, releases, etc.
"""

from .issues import GitHubIssuesExtractor

__all__ = [
    "GitHubIssuesExtractor",
]