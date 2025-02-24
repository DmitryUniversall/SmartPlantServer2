from src.app.bases.db import BaseSchema
from src.app.main.components.storage.entities.channel_message.schemas import StorageChannelMessage


class ListenChannelResponsePayload(BaseSchema):
    messages: tuple[StorageChannelMessage, ...]
