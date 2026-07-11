from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class DiscordUserModel(BaseModel):
    id: str
    username: str
    discriminator: str
    bot: Optional[bool] = False

class DiscordReactionModel(BaseModel):
    count: int
    emoji: Dict[str, Any]

class DiscordMessageModel(BaseModel):
    id: str
    channel_id: str
    author: DiscordUserModel
    content: str
    timestamp: datetime
    edited_timestamp: Optional[datetime] = None
    mention_everyone: bool
    reactions: List[DiscordReactionModel] = []
    attachments: List[Dict[str, Any]] = []
    thread: Optional[Dict[str, Any]] = None # If message started a thread

    @property
    def upvote_count(self) -> int:
        """Calculates total upvotes for Feature Request ranking."""
        upvotes = 0
        for reaction in self.reactions:
            emoji_name = reaction.emoji.get("name", "")
            if emoji_name in ["👍", "+1", "upvote"]:
                upvotes += reaction.count
        return upvotes

    @property
    def is_human(self) -> bool:
        return not self.author.bot