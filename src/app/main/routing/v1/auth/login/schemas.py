from pydantic import Field

from src.app.bases.db import BaseSchema
from src.app.main.components.auth.entities.auth_session import AuthSessionPrivate
from src.app.main.components.auth.entities.user import UserPrivate


class LoginRequestPayload(BaseSchema):
    username: str
    session_name: str
    password: str = Field(..., max_length=50)


class LoginResponsePayload(BaseSchema):
    user: UserPrivate
    session: AuthSessionPrivate
    access_token: str  # TODO: Use AuthTokenPair?
    refresh_token: str
