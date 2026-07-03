import requests
from requests.auth import HTTPBasicAuth

def create_jira_ticket(domain: str, email: str, token: str, project_key: str, summary: str, description: str):
    # Jira REST API v2 URL for creating issues
    url = f"https://{domain}.atlassian.net/rest/api/2/issue"
    
    auth = HTTPBasicAuth(email, token)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Building the ticket payload
    payload = {
        "fields": {
            "project": {"key": project_key},
            "summary": summary[:255], # Jira has a 255 character limit for titles
            "description": description,
            "issuetype": {"name": "Task"} # By default creating it as a Task
        }
    }
    
    response = requests.post(url, json=payload, headers=headers, auth=auth)
    
    if response.status_code == 201:
        issue_key = response.json().get('key')
        return {
            "status": "success", 
            "ticket_url": f"https://{domain}.atlassian.net/browse/{issue_key}",
            "key": issue_key
        }
    else:
        print(f"[Jira Error] {response.text}")
        return {"status": "error", "message": response.text}