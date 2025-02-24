from pydantic import Field

from src.app.bases.db import BaseSchema


class RefreshRequestPayload(BaseSchema):
    refresh_token: str = Field(..., max_length=1000)


class RefreshResponsePayload(BaseSchema):
    access_token: str
    refresh_token: str
