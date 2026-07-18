import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def extract_message_reactions(client, channel_id: str, timestamp: str) -> Optional[Dict[str, Any]]:
    """Fetches reactions for a specific message to gauge sentiment."""
    try:
        response = await client.reactions_get(channel=channel_id, timestamp=timestamp)
        if not response.get("ok"):
            logger.error(f"Slack API Error: {response.get('error')}")
            return None
            
        # Returns the message block which includes a 'reactions' array
        return response.get("message", {}).get("reactions", [])
    except Exception as e:
        logger.error(f"Error extracting reactions: {str(e)}")
        return None