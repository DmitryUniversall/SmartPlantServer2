from uuid import uuid4

from pydantic import Field, field_validator

from src.app.main.components.storage.models.direct_message.intent import StorageDirectMessageIntent
from src.app.main.components.storage.models.storage_message import StorageMessage
from src.core.utils.types import UUIDString


class StorageDirectMessage(StorageMessage):
    uuid: UUIDString = Field(default_factory=lambda x: str(uuid4()))
    intent: StorageDirectMessageIntent

    # noinspection PyNestedDecorators
    @field_validator('intent', mode="before")
    @classmethod
    def set_token_type(cls, value: str | StorageDirectMessageIntent) -> StorageDirectMessageIntent:
        return StorageDirectMessageIntent(value) if isinstance(value, str) else value
