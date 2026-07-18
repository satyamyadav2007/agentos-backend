import logging
from typing import Optional
from ..models.message import SlackMessage
from ..models.thread import SlackThread

logger = logging.getLogger(__name__)

async def extract_thread_replies(client, channel_id: str, thread_ts: str) -> Optional[SlackThread]:
    """Fetches all replies for a specific thread_ts."""
    try:
        response = await client.conversations_replies(channel=channel_id, ts=thread_ts)
        if not response.get("ok"):
            logger.error(f"Slack API Error: {response.get('error')}")
            return None
            
        raw_messages = response.get("messages", [])
        if not raw_messages:
            return None
            
        # First message is the parent
        parent = SlackMessage(**raw_messages[0])
        parent.channel = channel_id
        
        replies = []
        reply_users = set()
        
        for msg in raw_messages[1:]:
            msg["channel"] = channel_id
            parsed_msg = SlackMessage(**msg)
            replies.append(parsed_msg)
            if parsed_msg.user:
                reply_users.add(parsed_msg.user)
                
        return SlackThread(
            channel_id=channel_id,
            thread_ts=thread_ts,
            parent_message=parent,
            replies=replies,
            reply_users=list(reply_users)
        )
    except Exception as e:
        logger.error(f"Error extracting thread {thread_ts}: {str(e)}")
        return None