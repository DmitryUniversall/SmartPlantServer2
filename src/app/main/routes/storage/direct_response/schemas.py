from src.app.bases.db import BaseSchema
from src.app.main.routes.storage.schemas import StorageDirectMessageCreatePayload
from src.core.utils.types import UUIDString


class RequestPayload(BaseSchema):
    message: StorageDirectMessageCreatePayload
    response_to_message_uuid: UUIDString
