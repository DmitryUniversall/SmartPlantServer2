from typing import Any

from src.app.main.models_global.application_response import ApplicationResponsePayload
from src.core.exceptions.base import BaseApplicationError


class ApplicationHTTPException[_contentT: Any](BaseApplicationError):
    """
    A custom exception class for handling HTTP errors with a response payload,
    status code, and optional headers.
    """

    def __init__(
            self,
            *,
            payload: ApplicationResponsePayload[_contentT],
            status_code: int,
            headers: dict[str, str] | None = None
    ) -> None:
        super().__init__(payload.message)

        self.payload: ApplicationResponsePayload = payload
        self.headers: dict[str, str] | None = headers
        self.status_code = status_code
