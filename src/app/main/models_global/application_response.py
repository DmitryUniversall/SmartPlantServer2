from typing import Any

from pydantic import field_serializer

from src.app.bases.db import BaseSchema
from src.core.utils.types import JsonDict


class ApplicationResponsePayload[_contentT: Any](BaseSchema):
    ok: bool = True
    application_status_code: int
    message: str
    data: _contentT | None = None

    # noinspection PyNestedDecorators
    @field_serializer('data')
    @classmethod
    def serialize_data(cls, value: _contentT | None) -> JsonDict | None:
        if value is None:
            return None

        return value.model_dump() if isinstance(value, BaseSchema) else value  # type: ignore
