from src.app.bases.db import BaseSchema
from src.app.main.components.storage.entities import StorageDirectMessage


class ListenDirectResponsePayload(BaseSchema):
    messages: tuple[StorageDirectMessage, ...]
