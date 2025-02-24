from datetime import datetime

from pydantic import Field

from src.app.bases.db import BaseSchema
from src.core.utils.types import UUIDString


class AuthSessionInternal(BaseSchema):
    session_uuid: UUIDString
    user_id: int
    is_active: bool = True
    access_token_uuid: str = Field(..., max_length=1000)
    refresh_token_uuid: str = Field(..., max_length=1000)
    session_name: str = Field(..., max_length=50)
    ip_address: str = Field(..., max_length=25)
    user_agent: str = Field(..., max_length=1000)
    created_at: datetime
    last_used: datetime
    expires_at: datetime


class AuthSessionPrivate(BaseSchema):
    session_uuid: UUIDString
    is_active: bool = True
    user_id: int
    session_name: str = Field(..., max_length=50)
    created_at: datetime
    last_used: datetime
    expires_at: datetime
