from abc import ABC

from src.app.main.exceptions import GenericApplicationHTTPException


class AuthHTTPException(GenericApplicationHTTPException, ABC):
    pass
