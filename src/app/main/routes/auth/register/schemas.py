from src.app.bases.db import BaseSchema
from src.app.main.components.auth.models.auth_session import AuthSessionPrivate
from src.app.main.components.auth.models.user import UserPrivate


class RegisterReqeustPayload(BaseSchema):
    username: str
    password: str
    session_name: str


class RegisterResponsePayload(BaseSchema):
    user: UserPrivate
    session: AuthSessionPrivate
    access_token: str
    refresh_token: str
