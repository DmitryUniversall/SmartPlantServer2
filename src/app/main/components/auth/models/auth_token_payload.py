from datetime import datetime
from enum import Enum
from typing import Union
from uuid import uuid4

from pydantic import Field, field_validator

from src.app.bases.db import BaseSchema
from src.core.utils.types import UUIDString


class AuthTokenType(Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class AuthTokenPayload(BaseSchema):
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    token_type: AuthTokenType
    exp: datetime
    user_id: int
    session_uuid: UUIDString

    # noinspection PyNestedDecorators
    @field_validator('token_type', mode="before")
    @classmethod
    def set_token_type(cls, value: Union[str, AuthTokenType]) -> AuthTokenType:
        return AuthTokenType(value) if isinstance(value, str) else value
