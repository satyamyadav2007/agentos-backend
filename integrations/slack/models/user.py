from pydantic import BaseModel
from typing import Optional

class SlackUserProfile(BaseModel):
    real_name: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    image_512: Optional[str] = None
    title: Optional[str] = None # E.g., "Software Engineer"

class SlackUser(BaseModel):
    id: str
    team_id: str
    name: str
    deleted: bool = False
    real_name: Optional[str] = None
    tz: Optional[str] = None
    profile: Optional[SlackUserProfile] = None
    is_admin: Optional[bool] = False
    is_owner: Optional[bool] = False
    is_bot: Optional[bool] = False