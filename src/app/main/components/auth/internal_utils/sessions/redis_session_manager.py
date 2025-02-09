import asyncio
import logging
from datetime import datetime
from http import HTTPStatus

import pydantic

from src.app.main.components.auth.models.auth_session import AuthSessionInternal
from src.app.main.redis import RedisClientMixin
from src.app.main.utils.redis import convert_for_redis
from src.core.state import project_settings
from src.core.utils.singleton import ABCSingletonMeta
from src.core.utils.types import UUIDString
from .session_manager import AbstractSessionManager
from ..jwt_tools import create_jwt_token, calculate_refresh_expire_at
from ...exceptions import (
    InvalidSessionHTTPException,
    TokenInvalidHTTPException,
    AuthUserUnknownHTTPException,
    TokenExpiredHTTPException
)
from ...exceptions.generics import InactiveSessionHTTPException
from ...models.access_token_payload import AccessTokenPayload
from ...models.auth_token_payload import AuthTokenPayload
from ...models.refresh_token_payload import RefreshTokenPayload
from ...models.user.model import UserModel
from ...models.user.schema import UserInternal
from ...models.user.user_resource import UserResourceST

_logger = logging.getLogger(__name__)
_user_resource = UserResourceST()


class RedisSessionManager(RedisClientMixin, AbstractSessionManager, metaclass=ABCSingletonMeta):
    AUTH_USER_DATA_REDIS_KEY: str = project_settings.AUTH_REDIS_KEY + ":user:{}"
    AUTH_USER_SESSIONS_REDIS_KEY: str = AUTH_USER_DATA_REDIS_KEY + ":sessions"
    AUTH_USER_SESSION_REDIS_KEY: str = AUTH_USER_SESSIONS_REDIS_KEY + ":{}"

    def __init__(self) -> None:
        super().__init__(db=project_settings.AUTH_REDIS_DB_ID)

    def get_session_key(self, user_id: int, session_uuid: UUIDString) -> str:
        return self.AUTH_USER_SESSION_REDIS_KEY.format(user_id, session_uuid)

    def get_user_sessions_key(self, user_id: int) -> UUIDString:
        return self.AUTH_USER_SESSIONS_REDIS_KEY.format(user_id)

    async def __save_session(self, session: AuthSessionInternal) -> None:
        redis = await self.get_redis()

        session_key = self.get_session_key(session.user_id, session.session_uuid)
        await redis.hset(session_key, mapping=convert_for_redis(session.to_json_dict()))  # type: ignore
        await redis.expire(session_key, round(session.expires_at.timestamp()))  # type: ignore

    async def __delete_session(self, user_id: int, session_uuid: UUIDString, *, soft: bool) -> None:
        redis = await self.get_redis()
        session_key = self.get_session_key(user_id, session_uuid)

        if not await redis.exists(session_key):
            raise InvalidSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        if not soft:
            await redis.delete(session_key)
            return

        # Soft delete: update the "is_active" field to False
        await redis.hset(session_key, "is_active", "false")  # type: ignore

    async def __get_session(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal:
        redis = await self.get_redis()
        session_key = self.get_session_key(user_id, session_uuid)

        session_data = await redis.hgetall(session_key)  # type: ignore
        if not session_data:
            raise InvalidSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        session = AuthSessionInternal.model_validate(session_data)
        if not session.is_active:
            raise InactiveSessionHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return session

    async def __decode_access_token(self, token: str) -> AccessTokenPayload:
        try:
            return AccessTokenPayload.model_validate(self.decode_jwt_token(token))
        except pydantic.ValidationError as error:
            raise TokenInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error

    async def __decode_refresh_token(self, token: str) -> RefreshTokenPayload:
        try:
            return RefreshTokenPayload.model_validate(self.decode_jwt_token(token))
        except pydantic.ValidationError as error:
            raise TokenInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error

    async def __get_user_from_token_payload(self, payload: AuthTokenPayload) -> UserInternal:
        try:
            user_model = await _user_resource.get_by_pk(payload.user_id)
            return user_model.to_schema(scheme_cls=UserInternal)
        except UserModel.DoesNotExist as error:
            raise AuthUserUnknownHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error

    async def __scan_for_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        redis = await self.get_redis()

        session_uuids = tuple(
            key async for key in redis.scan_iter(match=self.get_user_sessions_key(user_id)))  # type: ignore
        sessions = await asyncio.gather(*(redis.hgetall(key) for key in session_uuids))  # type: ignore

        return tuple(map(AuthSessionInternal.model_validate, sessions))

    async def __create_access_token(self, *, payload: AccessTokenPayload) -> str:
        return create_jwt_token(payload=payload.to_json_dict(exclude='exp'), exp=payload.exp.timestamp())

    async def __create_refresh_token(self, *, payload: RefreshTokenPayload) -> str:
        return create_jwt_token(payload=payload.to_json_dict(exclude='exp'), exp=payload.exp.timestamp())

    async def create_session(
            self,
            user_id: int,
            ip_address: str,
            user_agent: str,
            session_name: str,
            access_token_expires_at: datetime | None = None,
            refresh_token_expires_at: datetime | None = None
    ) -> AuthSessionInternal:
        session_uuid = self.generate_session_uuid()
        session = AuthSessionInternal(
            session_uuid=session_uuid,
            user_id=user_id,
            access_token=await self.generate_access_token(user_id, session_uuid, access_token_expires_at),
            refresh_token=await self.generate_refresh_token(user_id, session_uuid, refresh_token_expires_at),
            session_name=session_name,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(),
            last_used=datetime.now(),
            expires_at=datetime.now()
        )

        await self.__save_session(session)
        return session

    async def validate_access_token(self, access_token: str) -> AuthSessionInternal:
        payload = await self.__decode_access_token(access_token)
        session = await self.__get_session(payload.user_id, payload.session_uuid)

        if session.access_token != access_token:
            raise TokenExpiredHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return session

    async def validate_refresh_token(self, refresh_token: str) -> AuthSessionInternal:
        payload = await self.__decode_refresh_token(refresh_token)
        session = await self.__get_session(payload.user_id, payload.session_uuid)

        if session.refresh_token != refresh_token:
            raise TokenExpiredHTTPException(status_code=HTTPStatus.UNAUTHORIZED)

        return session

    async def get_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        return await self.__scan_for_user_sessions(user_id)

    async def get_session(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal:
        return await self.__get_session(user_id, session_uuid)

    async def rotate_session_tokens(self, session: AuthSessionInternal) -> None:
        session.access_token = await self.generate_access_token(session.user_id, session.session_uuid)
        session.refresh_token = await self.generate_refresh_token(session.user_id, session.session_uuid)
        session.expires_at = calculate_refresh_expire_at()  # TODO: Pass expires_at here
        await self.update_session(session)

    async def rotate_session_tokens_by_id(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal:
        session = await self.get_session(user_id, session_uuid)
        await self.rotate_session_tokens(session)
        return session

    async def refresh_session(self, refresh_token: str) -> AuthSessionInternal:
        session = await self.validate_refresh_token(refresh_token)
        await self.rotate_session_tokens(session)
        return session

    async def revoke_session(self, user_id: int, session_uuid: UUIDString) -> None:
        await self.__delete_session(user_id, session_uuid, soft=True)

    async def revoke_other_sessions(self, user_id: int, keep_session_uuid: UUIDString) -> None:
        for session in await self.get_user_sessions(user_id):
            await self.__delete_session(user_id, session.session_uuid, soft=True)

    async def update_session(self, updated_schema: AuthSessionInternal) -> None:
        await self.__save_session(updated_schema)

    async def session_heartbeat(self, session: AuthSessionInternal) -> None:
        session.last_used = datetime.now()
        await self.update_session(session)

    async def session_heartbeat_by_id(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal:
        session = await self.get_session(user_id, session_uuid)
        await self.session_heartbeat(session)
        return session

    async def generate_access_token(self, user_id: int, session_uuid: UUIDString, expires_at: datetime | None = None) -> str:
        payload = AccessTokenPayload(user_id=user_id, session_uuid=session_uuid)

        if expires_at is not None:
            payload.exp = expires_at

        return await self.__create_access_token(payload=payload)

    async def generate_refresh_token(self, user_id: int, session_uuid: UUIDString, expires_at: datetime | None = None) -> str:
        payload = RefreshTokenPayload(user_id=user_id, session_uuid=session_uuid)

        if expires_at is not None:
            payload.exp = expires_at

        return await self.__create_refresh_token(payload=payload)

    async def cleanup(self) -> None:  # TODO
        pass
