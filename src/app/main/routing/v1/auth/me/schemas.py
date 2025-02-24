from src.app.bases.db import BaseSchema
from src.app.main.components.auth.entities.user import UserPrivate


class GetMeResponsePayload(BaseSchema):
    user: UserPrivate
