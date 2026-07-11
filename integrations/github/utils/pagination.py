from typing import List, Dict, Any, Callable, Awaitable

class GitHubPaginator:
    """Helper to fetch all pages of a GitHub API response."""

    @staticmethod
    async def fetch_all(
        fetch_function: Callable[[int], Awaitable[List[Dict[str, Any]]]], 
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Keeps fetching pages until an empty list is returned or max_pages is reached.
        fetch_function must accept a 'page' integer and return a list.
        """
        all_results = []
        page = 1
        
        while page <= max_pages:
            results = await fetch_function(page)
            if not results:
                break
                
            all_results.extend(results)
            
            # If we received less than 100 (standard per_page max), we are on the last page
            if len(results) < 100:
                break
                
            page += 1
            
        return all_results