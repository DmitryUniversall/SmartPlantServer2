from pydantic import Field

from src.app.bases.db import BaseSchema
from src.app.main.components.storage.models import StorageChannelMessage
from src.core.utils.types import JsonDict


class StorageChannelMessageCreatePayload(BaseSchema):
    intent: str = Field(..., max_length=50)
    sender_name: str = Field(..., max_length=50)
    target_name: str = Field(..., max_length=50)
    data: JsonDict


class WriteToChannelRequestPayload(BaseSchema):
    message: StorageChannelMessageCreatePayload


class WriteToChannelResponsePayload(BaseSchema):
    message: StorageChannelMessage
