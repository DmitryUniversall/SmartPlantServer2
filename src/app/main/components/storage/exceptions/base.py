from abc import ABC

from src.app.main.exceptions import GenericApplicationHTTPException


class StorageHTTPException(GenericApplicationHTTPException, ABC):
    pass
