import logging
from typing import List, Optional
from ..models.channel import SlackChannel

logger = logging.getLogger(__name__)

async def extract_channels(client, types: str = "public_channel,private_channel", limit: int = 100) -> List[SlackChannel]:
    """Fetches channels from the workspace."""
    channels_list = []
    cursor: Optional[str] = None
    
    try:
        while True:
            response = await client.conversations_list(types=types, limit=limit, cursor=cursor)
            if not response.get("ok"):
                logger.error(f"Slack API Error: {response.get('error')}")
                break
                
            for channel in response.get("channels", []):
                channels_list.append(SlackChannel(**channel))
                
            cursor = response.get("response_metadata", {}).get("next_cursor")
            if not cursor:
                break
                
        return channels_list
    except Exception as e:
        logger.error(f"Error extracting channels: {str(e)}")
        return []