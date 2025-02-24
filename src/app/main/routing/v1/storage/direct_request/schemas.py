from pydantic import Field

from src.app.bases.db import BaseSchema
from src.app.main.components.storage.entities import StorageDirectResponse
from src.app.main.routing.v1.storage.schemas import StorageDirectMessageCreatePayload


class RequestPayload(BaseSchema):
    message: StorageDirectMessageCreatePayload
    timeout: int = Field(le=30)


class ResponsePayload(BaseSchema):
    responded: bool
    response: StorageDirectResponse | None
