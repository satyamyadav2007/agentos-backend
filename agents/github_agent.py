from github import Github
import datetime

async def fetch_recent_issues(repo_name: str, access_token: str, days=30):
    g = Github(access_token)
    repo = g.get_repo(repo_name)
    
    cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)
    
    # Fetching issues updated in the last 30 days
    issues = repo.get_issues(state='all', since=cutoff_date)
    
    standardized_data = []
    for issue in issues:
        # Ignore pull requests, only keep real issues
        if not issue.pull_request: 
            standardized_data.append({
                "source": "GitHub",
                "id": issue.number,
                "text": f"{issue.title}: {issue.body}",
                "user": issue.user.login,
                "labels": [label.name for label in issue.labels]
            })
            
    return standardized_data