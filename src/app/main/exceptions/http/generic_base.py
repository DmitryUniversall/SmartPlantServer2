from abc import abstractmethod, ABC
from http import HTTPStatus
from typing import Any

from src.app.main.models_global import ApplicationResponsePayload
from .base import ApplicationHTTPException


class GenericApplicationHTTPException[_contentT: Any](ApplicationHTTPException[_contentT], ABC):
    """
    A generic exception class for HTTP errors that includes a customizable response payload.
    """

    def __init__(
            self,
            *,
            payload: ApplicationResponsePayload[_contentT] | None = None,
            status_code: int = HTTPStatus.NOT_FOUND,
            headers: dict[str, str] | None = None,
            **payload_kwargs
    ) -> None:
        if payload is None:
            payload = self.get_default_response_payload(**payload_kwargs)

        super().__init__(payload=payload, status_code=status_code, headers=headers)

    @abstractmethod
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload[_contentT]:
        """
        Abstract method for generating the default response payload for the exception.

        :param payload_kwargs: `dict`
            Additional keyword arguments for customizing the default response payload.

        :return: `ApplicationResponsePayload[_contentT]`
            The default payload for the error response.
        """
