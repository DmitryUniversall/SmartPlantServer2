from src.app.bases.db import BaseSchema
from src.app.main.components.storage.models.channel_message.schema import StorageChannelMessage


class ListenChannelResponsePayload(BaseSchema):
    messages: tuple[StorageChannelMessage, ...]
