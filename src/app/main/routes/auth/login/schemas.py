from src.app.bases.db import BaseSchema
from src.app.main.components.auth.models.auth_session import AuthSessionPrivate
from src.app.main.components.auth.models.auth_token_pair import AuthTokenPair
from src.app.main.components.auth.models.user import UserPrivate


class LoginRequestPayload(BaseSchema):
    username: str
    password: str
    session_name: str


class LoginResponsePayload(BaseSchema):
    user: UserPrivate
    session: AuthSessionPrivate
    access_token: str
    refresh_token: str
