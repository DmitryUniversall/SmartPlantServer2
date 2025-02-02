from .base import AuthHTTPException
from .generics import (
    AuthorizationNotSpecifiedHTTPException,
    AuthorizationInvalidHTTPException,
    AuthorizationTypeUnknownHTTPException,
    TokenNotSpecifiedHTTPException,
    TokenExpiredHTTPException,
    TokenInvalidHTTPException,
    TokenValidationFailed,
    AuthUserUnknownHTTPException,
    AuthUserAlreadyExists,
    WrongAuthCredentialsHTTPException,
    InvalidSessionHTTPException,
    SuspiciousActivityHTTPException
)
