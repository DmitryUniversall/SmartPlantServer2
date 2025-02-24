from pydantic import Field

from src.app.main.components.storage.entities.storage_message import StorageMessage


class StorageChannelMessage(StorageMessage):
    id: int
    intent: str = Field(..., max_length=50)  # TODO: Validate it (must not start/end with __)
    channel_name: str = Field(..., max_length=50)  # TODO: Validate it (must not start/end with __)
