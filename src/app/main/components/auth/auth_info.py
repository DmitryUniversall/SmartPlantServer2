from src.app.bases.db import BaseSchema
from src.app.main.components.auth.models.auth_session import AuthSessionInternal
from src.app.main.components.auth.models.user.schemas import UserInternal


class AuthInfo(BaseSchema):
    user: UserInternal
    session: AuthSessionInternal
