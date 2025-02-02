from http import HTTPStatus

from pydantic import ValidationError

from src.app.main.models_global import ApplicationResponsePayload
from src.core.state import project_settings
from .generic_base import GenericApplicationHTTPException


class ForbiddenHTTPException(GenericApplicationHTTPException):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, status_code=HTTPStatus.FORBIDDEN)

    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.FORBIDDEN,
            **payload_kwargs
        })


class NotFoundHTTPException(GenericApplicationHTTPException):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, status_code=HTTPStatus.NOT_FOUND)

    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.NOT_FOUND,
            **payload_kwargs
        })


class BadRequestHTTPException(GenericApplicationHTTPException):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, status_code=HTTPStatus.BAD_REQUEST)

    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.BAD_REQUEST,
            **payload_kwargs
        })


class UnprocessableEntityHTTPException(GenericApplicationHTTPException):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs, status_code=HTTPStatus.UNPROCESSABLE_ENTITY)

    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.UNPROCESSABLE_ENTITY,
            **payload_kwargs
        })


class SchemaValidationHTTPException(UnprocessableEntityHTTPException):
    def __init__(self, validation_error: ValidationError | None = None, **kwargs) -> None:
        self._validation_error: ValidationError | None = validation_error
        super().__init__(**kwargs)

    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        payload = super().get_default_response_payload(**payload_kwargs)

        if self._validation_error is not None:
            payload.data = {
                "detail": [
                    {"field": e["loc"][-1], "message": e["msg"]} for e in self._validation_error.errors()  # type: ignore
                ]
            }

        return payload
