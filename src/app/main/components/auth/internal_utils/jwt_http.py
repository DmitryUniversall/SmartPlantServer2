from http import HTTPStatus

import jwt
import pydantic

from src.app.main.components.auth.entities.auth_token_payload.schemas import AccessTokenPayload, RefreshTokenPayload, AuthTokenPayload
from src.app.main.components.auth.entities.user import UserInternal, UserModel
from src.app.main.components.auth.exceptions import TokenExpiredHTTPException, TokenInvalidHTTPException, AuthUserUnknownHTTPException
from src.app.main.components.auth.internal_utils.jwt_tools import decode_jwt_token
from src.app.main.components.auth.services.user.user_service import UserServiceST
from src.core.utils.types import JsonDict

_user_service = UserServiceST()


def decode_jwt_token_with_http_exceptions(token: str) -> JsonDict:
    try:
        return decode_jwt_token(token)
    except jwt.ExpiredSignatureError as error:
        raise TokenExpiredHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error
    except jwt.PyJWTError as error:
        raise TokenInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error


def decode_access_token_with_http_exceptions(token: str) -> AccessTokenPayload:
    try:
        return AccessTokenPayload.model_validate(decode_jwt_token_with_http_exceptions(token))
    except pydantic.ValidationError as error:
        raise TokenInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error


def decode_refresh_token_with_http_exceptions(token: str) -> RefreshTokenPayload:
    try:
        return RefreshTokenPayload.model_validate(decode_jwt_token_with_http_exceptions(token))
    except pydantic.ValidationError as error:
        raise TokenInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error


async def get_user_from_token_payload(payload: AuthTokenPayload) -> UserInternal:
    try:
        user_model = await _user_service.get_user_by_id(payload.user_id)
        return user_model.to_schema(scheme_cls=UserInternal)
    except UserModel.DoesNotExist as error:
        raise AuthUserUnknownHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error
