from abc import ABC, abstractmethod
from functools import reduce
from typing import Any

from starlette.background import BackgroundTask

from src.app.main.http.responses.application_json_response import ApplicationJsonResponse
from src.app.main.models_global import ApplicationResponsePayload
from src.core.state import project_settings


class BaseGenericApplicationJsonResponse[_contentT: Any](ApplicationJsonResponse[_contentT], ABC):
    """
    An abstract base class for generic application JSON responses with customizable payloads.
    """

    def __init__(
            self,
            *,
            status_code: int,
            payload: ApplicationResponsePayload | None = None,
            headers: dict[str, str] | None = None,
            background: BackgroundTask | None = None,
            **payload_kwargs
    ) -> None:
        """
        Initializes the response with the given status code, payload, and additional parameters.

        :param status_code: `int`
            The HTTP status code for the response.

        :param payload: `ApplicationResponsePayload | None`
            The content of the response, which is an instance of `ApplicationResponsePayload`.
            If not provided, `get_default_response_payload` will be called to generate it.

        :param headers: `dict[str, str] | None`
            Optional headers for the response.

        :param background: `BackgroundTask | None`
            Optional background task to be executed after the response is sent.

        :param payload_kwargs: `**payload_kwargs`
            Additional keyword arguments for generating the default response payload.
        """

        if payload is None:
            payload = self.get_default_response_payload(**payload_kwargs)

        super().__init__(content=payload, status_code=status_code, headers=headers, background=background)

    @abstractmethod
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        """
        Abstract method for generating the default response payload.

        :param payload_kwargs: `**payload_kwargs`
            Additional arguments that can be passed to customize the payload.

        :return: `ApplicationResponsePayload`
            The default response payload for this response.
        """


class GenericApplicationJsonResponse(BaseGenericApplicationJsonResponse):
    """
    A concrete implementation of `BaseGenericApplicationJsonResponse` that generates
    a response with default status and payload based on class-level settings.

    Static attributes:
    - `default_ok`: `int`
        The default `ok` status for the response (usually `1` for success).

    - `default_status_code`: `int`
        The default HTTP status code for the response.

    - `default_status_info_path`: `str`
        A path string used to extract status information from the global settings.
    """

    default_ok: int
    default_status_code: int
    default_status_info_path: str

    def __init__(self, **kwargs) -> None:
        """
        Initializes the response using default class-level settings and any provided arguments.

        :param kwargs: `**kwargs`
            Keyword arguments passed to the parent `__init__` method.
        """

        kwargs.setdefault("status_code", getattr(self.__class__, "default_status_code"))
        super().__init__(**kwargs)

    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        """
        Generates the default response payload based on class-level default settings.

        :param payload_kwargs: `**payload_kwargs`
            Additional arguments to customize the response payload.

        :return: `ApplicationResponsePayload`
            The default response payload.
        """

        path = getattr(self.__class__, "default_status_info_path").split(".")
        default_status_info = reduce(getattr, path, project_settings.APPLICATION_STATUS_CODES)

        return ApplicationResponsePayload(**{
            "ok": getattr(self.__class__, "default_ok"),
            **default_status_info,
            **payload_kwargs
        })
