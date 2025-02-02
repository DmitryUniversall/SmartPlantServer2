from http import HTTPStatus
from typing import Optional

from src.app.main.components.auth.exceptions import (
    AuthorizationNotSpecifiedHTTPException,
    AuthorizationInvalidHTTPException,
    AuthorizationTypeUnknownHTTPException,
    TokenNotSpecifiedHTTPException
)
from src.core.state import project_settings


class BearerAuthMixin:
    async def extract_token(self, header: Optional[str]) -> str:
        _auth_status_codes = project_settings.APPLICATION_STATUS_CODES.AUTH

        if not header:
            raise AuthorizationNotSpecifiedHTTPException(status_code=HTTPStatus.UNAUTHORIZED)
        elif len(header.split(" ")) != 2:
            raise AuthorizationInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        type_, access_token = header.split(" ")
        if type_.lower() != "bearer":
            raise AuthorizationTypeUnknownHTTPException(status_code=HTTPStatus.UNAUTHORIZED)
        elif not access_token:
            raise TokenNotSpecifiedHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return access_token
