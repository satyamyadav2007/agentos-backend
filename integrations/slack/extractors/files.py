import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

async def extract_file_info(client, file_id: str) -> Optional[Dict[str, Any]]:
    """Fetches metadata about a file shared in Slack (e.g., error logs)."""
    try:
        response = await client.files_info(file=file_id)
        if not response.get("ok"):
            logger.error(f"Slack API Error: {response.get('error')}")
            return None
            
        return response.get("file", {})
    except Exception as e:
        logger.error(f"Error extracting file info for {file_id}: {str(e)}")
        return None