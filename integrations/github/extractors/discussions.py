from typing import List, Dict, Any

class GitHubDiscussionsExtractor:
    """Handles data collection for GitHub Discussions using GraphQL."""
    
    def __init__(self, client):
        self.client = client

    async def fetch_recent_discussions(self, repo_full_name: str, limit: int = 15) -> List[Dict[str, Any]]:
        print(f"💬 [GitHub Extractor] Scanning Discussions for {repo_full_name} via GraphQL...")
        
        try:
            # Split 'owner/repo_name' for the GraphQL Query
            owner, name = repo_full_name.split("/")
            
            # The official GitHub GraphQL Query for Discussions
            graphql_query = """
            query {
              repository(owner: "%s", name: "%s") {
                discussions(first: %d, orderBy: {field: CREATED_AT, direction: DESC}) {
                  nodes {
                    id
                    title
                    bodyText
                    url
                    createdAt
                    author { login }
                    category { name }
                  }
                }
              }
            }
            """ % (owner, name, limit)
            
            # Assuming your base client has a post method, or you can use httpx/requests here
            # Endpoint for GraphQL is always https://api.github.com/graphql
            raw_data = await self.client.post("graphql", json={"query": graphql_query})
            
            # Parse GraphQL response tree
            discussions = raw_data.get("data", {}).get("repository", {}).get("discussions", {}).get("nodes", [])
            
            print(f"   ✅ Successfully extracted {len(discussions)} discussions from {repo_full_name}")
            return discussions
            
        except Exception as e:
            print(f"🚨 [GitHub Extractor] Failed to fetch discussions for {repo_full_name}: {e}")
            return []