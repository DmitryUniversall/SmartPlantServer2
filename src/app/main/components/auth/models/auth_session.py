from datetime import datetime

from src.app.bases.db import BaseSchema
from src.core.utils.types import UUIDString


class AuthSessionInternal(BaseSchema):
    session_id: UUIDString
    user_id: int
    access_token: str  # TODO: Store token_uuid instead of token itself
    refresh_token: str
    session_name: str  # TODO: Validate session name (make it unique?)
    ip_address: str
    user_agent: str
    is_active: bool = True
    created_at: datetime
    last_used: datetime
    expires_at: datetime


class AuthSessionPrivate(BaseSchema):
    session_id: UUIDString
    user_id: int
    session_name: str
    is_active: bool = True
    created_at: datetime
    last_used: datetime
    expires_at: datetime
