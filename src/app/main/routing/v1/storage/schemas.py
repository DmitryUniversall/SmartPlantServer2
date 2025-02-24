from pydantic import Field

from src.app.bases.db import BaseSchema
from src.core.utils.types import JsonDict


class StorageDirectMessageCreatePayload(BaseSchema):
    sender_name: str = Field(..., max_length=50)
    target_name: str = Field(..., max_length=50)
    data: JsonDict
