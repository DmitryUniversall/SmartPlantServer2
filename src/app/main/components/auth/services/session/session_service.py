from abc import ABCMeta
from http import HTTPStatus

from src.app.main.components.auth.entities.auth_session import AuthSessionInternal
from src.app.main.components.auth.exceptions import InvalidSessionHTTPException, TokenExpiredHTTPException
from src.app.main.components.auth.exceptions.generics import InactiveSessionHTTPException
from src.app.main.components.auth.internal_utils.jwt_http import decode_access_token_with_http_exceptions, decode_refresh_token_with_http_exceptions
from src.app.main.components.auth.repositories.session.redis_session_repository import RedisSessionRepository
from src.core.utils.types import UUIDString


class SessionServiceST(metaclass=ABCMeta):
    def __init__(self) -> None:
        self._session_repository = RedisSessionRepository()

    async def get_session(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal:
        if (session := await self._session_repository.get_session(user_id, session_uuid)) is None:
            raise InvalidSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if not session.is_active:
            raise InactiveSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return session

    async def validate_access_token(self, access_token: str) -> AuthSessionInternal:
        payload = decode_access_token_with_http_exceptions(access_token)

        if (session := await self.get_session(payload.user_id, payload.session_uuid)) is None:
            raise InvalidSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if session.access_token_uuid != payload.token_uuid:
            raise TokenExpiredHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return session

    async def validate_refresh_token(self, refresh_token: str) -> AuthSessionInternal:
        payload = decode_refresh_token_with_http_exceptions(refresh_token)

        if (session := await self.get_session(payload.user_id, payload.session_uuid)) is None:
            raise InvalidSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if session.refresh_token_uuid != payload.token_uuid:
            raise TokenExpiredHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return session

    async def revoke_session(self, user_id: int, session_uuid: UUIDString) -> None:
        success = await self._session_repository.revoke_session_by_id(user_id, session_uuid)
        if not success:
            raise InvalidSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

    async def create_session(
            self,
            user_id: int,
            ip_address: str,
            user_agent: str,
            session_name: str,
            access_token_uuid: UUIDString,
            refresh_token_uuid: UUIDString
    ) -> AuthSessionInternal:
        return await self._session_repository.create_session(
            user_id, ip_address, user_agent, session_name, access_token_uuid, refresh_token_uuid
        )

    async def get_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        return await self._session_repository.get_user_sessions(user_id)

    async def update_session(self, updated_session: AuthSessionInternal) -> None:
        await self._session_repository.update_session(updated_session)

    async def revoke_other_sessions(self, user_id: int, keep_session_uuid: UUIDString) -> None:
        return await self._session_repository.revoke_other_sessions(user_id, keep_session_uuid)
