from datetime import datetime

from pydantic import Field

from src.app.bases.db import BaseSchema
from src.core.utils.types import JsonDict


class StorageMessage(BaseSchema):
    user_id: int
    sender_name: str = Field(..., max_length=50)  # TODO: Validate it (must not start/end with __)
    target_name: str = Field(..., max_length=50)  # TODO: Validate it (must not start/end with __)
    created_at: datetime = Field(default_factory=datetime.now)
    data: JsonDict
