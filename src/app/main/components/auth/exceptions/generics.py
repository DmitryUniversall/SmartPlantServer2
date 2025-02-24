from src.app.main.models_global import ApplicationResponsePayload
from src.core.state import project_settings
from .base import AuthHTTPException


class AuthorizationNotSpecifiedHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.AUTHORIZATION_NOT_SPECIFIED,
            **payload_kwargs
        })


class AuthorizationInvalidHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.AUTHORIZATION_INVALID,
            **payload_kwargs
        })


class AuthorizationTypeUnknownHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.AUTHORIZATION_TYPE_UNKNOWN,
            **payload_kwargs
        })


class TokenNotSpecifiedHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.TOKEN_NOT_SPECIFIED,
            **payload_kwargs
        })


class TokenExpiredHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.TOKEN_EXPIRED,
            **payload_kwargs
        })


class TokenInvalidHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.TOKEN_INVALID,
            **payload_kwargs
        })


class TokenValidationFailed(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.TOKEN_VALIDATION_FAILED,
            **payload_kwargs
        })


class AuthUserUnknownHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.UNKNOWN_USER,
            **payload_kwargs
        })


class UserAlreadyExists(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.ALREADY_EXISTS,
            **payload_kwargs
        })


class WrongAuthCredentialsHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.WRONG_AUTH_CREDENTIALS,
            **payload_kwargs
        })


class InvalidSessionHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.INVALID_SESSION,
            **payload_kwargs
        })


class SuspiciousActivityHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.SUSPICIOUS_ACTIVITY,
            **payload_kwargs
        })


class InactiveSessionHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.INACTIVE_SESSION,
            **payload_kwargs
        })


class AuthFailedUnknownErrorHTTPException(AuthHTTPException):
    def get_default_response_payload(self, **payload_kwargs) -> ApplicationResponsePayload:
        return ApplicationResponsePayload(**{
            "ok": False,
            **project_settings.APPLICATION_STATUS_CODES.AUTH.AUTH_FAILED_UNKNOWN_ERROR,
            **payload_kwargs
        })
