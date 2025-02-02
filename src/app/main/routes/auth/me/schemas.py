from src.app.bases.db import BaseSchema
from src.app.main.components.auth.models.user import UserPrivate


class GetMeResponsePayload(BaseSchema):
    user: UserPrivate
