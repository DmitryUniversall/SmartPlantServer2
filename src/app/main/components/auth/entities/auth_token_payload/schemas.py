from datetime import datetime
from typing import Union, Literal
from uuid import uuid4

from pydantic import Field, field_validator

from src.app.bases.db import BaseSchema
from src.app.main.components.auth.entities.auth_token_payload.auth_token_type import AuthTokenType
from src.app.main.components.auth.internal_utils.jwt_tools import calculate_refresh_expire_at, calculate_access_expire_at
from src.core.utils.types import UUIDString


class AuthTokenPayload(BaseSchema):
    token_uuid: str = Field(default_factory=lambda: str(uuid4()))
    token_type: AuthTokenType
    exp: datetime
    user_id: int
    session_uuid: UUIDString

    # noinspection PyNestedDecorators
    @field_validator('token_type', mode="before")
    @classmethod
    def set_token_type(cls, value: Union[str, AuthTokenType]) -> AuthTokenType:
        return AuthTokenType(value) if isinstance(value, str) else value


class RefreshTokenPayload(AuthTokenPayload):
    token_type: Literal[AuthTokenType.REFRESH] = AuthTokenType.REFRESH
    exp: datetime = Field(default_factory=calculate_refresh_expire_at)


class AccessTokenPayload(AuthTokenPayload):
    token_type: Literal[AuthTokenType.ACCESS] = AuthTokenType.ACCESS
    exp: datetime = Field(default_factory=calculate_access_expire_at)
