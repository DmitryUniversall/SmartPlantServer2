from src.app.bases.db import BaseSchema
from src.app.main.components.storage.models import StorageDirectMessage


class ListenDirectResponsePayload(BaseSchema):
    messages: tuple[StorageDirectMessage, ...]
