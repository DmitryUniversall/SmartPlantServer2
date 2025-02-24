from src.app.bases.db import BaseSchema
from src.app.main.components.auth.entities.auth_session import AuthSessionInternal
from src.app.main.components.auth.entities.user.schemas import UserInternal


class AuthInfo(BaseSchema):
    user: UserInternal
    session: AuthSessionInternal
