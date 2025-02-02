from pydantic import Field

from src.app.bases.db import BaseSchema
from src.app.main.components.auth.models.auth_session import AuthSessionPrivate
from src.app.main.components.auth.models.user import UserPrivate


class RegisterReqeustPayload(BaseSchema):
    username: str = Field(..., max_length=25)
    password: str = Field(..., max_length=50)
    session_name: str = Field(..., max_length=50)


class RegisterResponsePayload(BaseSchema):
    user: UserPrivate
    session: AuthSessionPrivate
    access_token: str
    refresh_token: str
