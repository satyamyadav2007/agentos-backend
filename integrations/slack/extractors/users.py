import logging
from typing import List, Optional
from ..models.user import SlackUser

logger = logging.getLogger(__name__)

async def extract_users(client, limit: int = 200) -> List[SlackUser]:
    """Fetches all users in the Slack workspace with pagination."""
    users_list = []
    cursor: Optional[str] = None
    
    try:
        while True:
            response = await client.users_list(limit=limit, cursor=cursor)
            if not response.get("ok"):
                logger.error(f"Slack API Error: {response.get('error')}")
                break
                
            for member in response.get("members", []):
                # Ignore deleted users and bots if needed, or just map them
                users_list.append(SlackUser(**member))
                
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
                
        return users_list
    except Exception as e:
        logger.error(f"Error extracting users: {str(e)}")
        return []