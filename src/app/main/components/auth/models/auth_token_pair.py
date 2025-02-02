from src.app.bases.db import BaseSchema


class AuthTokenPair(BaseSchema):
    access_token: str
    refresh_token: str
