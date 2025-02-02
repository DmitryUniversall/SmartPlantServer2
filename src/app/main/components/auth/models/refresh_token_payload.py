from datetime import datetime
from typing import Literal

from pydantic import Field

from .auth_token_payload import AuthTokenPayload, AuthTokenType
from ..internal_utils.jwt_tools import calculate_refresh_expire_at


class RefreshTokenPayload(AuthTokenPayload):
    token_type: Literal[AuthTokenType.REFRESH] = AuthTokenType.REFRESH
    exp: datetime = Field(default_factory=calculate_refresh_expire_at)
