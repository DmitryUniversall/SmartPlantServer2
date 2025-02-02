from src.app.bases.db import BaseSchema


class RefreshRequestPayload(BaseSchema):
    refresh_token: str


class RefreshResponsePayload(BaseSchema):
    access_token: str
    refresh_token: str
