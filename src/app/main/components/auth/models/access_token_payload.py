from datetime import datetime
from typing import Literal

from pydantic import Field

from .auth_token_payload import AuthTokenPayload, AuthTokenType
from ..internal_utils.jwt_tools import calculate_access_expire_at


class AccessTokenPayload(AuthTokenPayload):
    token_type: Literal[AuthTokenType.ACCESS] = AuthTokenType.ACCESS
    exp: datetime = Field(default_factory=calculate_access_expire_at)
