from pydantic import BaseModel
from typing import List
from .message import SlackMessage

class SlackThread(BaseModel):
    channel_id: str
    thread_ts: str
    parent_message: SlackMessage
    replies: List[SlackMessage] = []
    reply_users: List[str] = []