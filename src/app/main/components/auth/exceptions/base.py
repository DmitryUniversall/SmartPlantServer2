from abc import ABC
from http import HTTPStatus

from src.app.main.exceptions import GenericApplicationHTTPException


class AuthHTTPException(GenericApplicationHTTPException, ABC):
    def __init__(self, **kwargs) -> None:
        kwargs.setdefault("status_code", HTTPStatus.UNAUTHORIZED)
        super().__init__(**kwargs)
