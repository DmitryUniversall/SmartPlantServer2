import asyncio
import logging
from datetime import datetime

from src.app.main.components.auth.entities.auth_session import AuthSessionInternal
from src.app.main.components.auth.internal_utils.jwt_tools import calculate_refresh_expire_at, create_access_token, create_refresh_token
from src.app.main.components.auth.repositories.user.user_repository import UserRepositoryST
from src.app.main.redis import RedisClientMixin
from src.app.main.utils.redis import convert_for_redis
from src.core.state import project_settings
from src.core.utils.singleton import ABCSingletonMeta
from src.core.utils.types import UUIDString
from .abc import AbstractSessionRepository

_logger = logging.getLogger(__name__)
_user_resource = UserRepositoryST()


class RedisSessionRepository(RedisClientMixin, AbstractSessionRepository, metaclass=ABCSingletonMeta):
    AUTH_USER_DATA_REDIS_KEY: str = project_settings.AUTH_REDIS_KEY + ":user:{}"
    AUTH_USER_SESSIONS_REDIS_KEY: str = AUTH_USER_DATA_REDIS_KEY + ":sessions"
    AUTH_USER_SESSION_REDIS_KEY: str = AUTH_USER_SESSIONS_REDIS_KEY + ":{}"

    def __init__(self) -> None:
        super().__init__(db=project_settings.AUTH_REDIS_DB_ID)

    def _get_session_key(self, user_id: int, session_uuid: UUIDString) -> str:
        return self.AUTH_USER_SESSION_REDIS_KEY.format(user_id, session_uuid)

    def _get_user_sessions_key(self, user_id: int) -> UUIDString:
        return self.AUTH_USER_SESSIONS_REDIS_KEY.format(user_id)

    async def __save_session(self, session: AuthSessionInternal) -> None:
        redis = await self.get_redis()

        session_key = self._get_session_key(session.user_id, session.session_uuid)
        await redis.hset(session_key, mapping=convert_for_redis(session.to_json_dict()))  # type: ignore
        await redis.expire(session_key, round(session.expires_at.timestamp()))  # type: ignore

    async def __delete_session(self, user_id: int, session_uuid: UUIDString, *, soft: bool) -> bool:
        redis = await self.get_redis()
        session_key = self._get_session_key(user_id, session_uuid)

        if not await redis.exists(session_key):
            return False

        if soft:
            # Soft delete: update the "is_active" field to False
            await redis.hset(session_key, "is_active", "false")  # type: ignore
        else:
            await redis.delete(session_key)

        return True

    async def __get_session(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        redis = await self.get_redis()
        session_key = self._get_session_key(user_id, session_uuid)

        if (session_data := await redis.hgetall(session_key)) is None:  # type: ignore
            return None

        return AuthSessionInternal.model_validate(session_data)

    async def __scan_for_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        redis = await self.get_redis()

        session_uuids = tuple(key async for key in redis.scan_iter(match=self._get_user_sessions_key(user_id)))  # type: ignore
        sessions = await asyncio.gather(*(redis.hgetall(key) for key in session_uuids))  # type: ignore

        return tuple(map(AuthSessionInternal.model_validate, sessions))

    async def create_session(
            self,
            user_id: int,
            ip_address: str,
            user_agent: str,
            session_name: str
    ) -> AuthSessionInternal:
        session_uuid = self.generate_session_uuid()
        access_token = create_access_token(user_id, session_uuid)
        refresh_token = create_refresh_token(user_id, session_uuid)

        session = AuthSessionInternal(
            session_uuid=session_uuid,
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            session_name=session_name,
            ip_address=ip_address,
            user_agent=user_agent,
            created_at=datetime.now(),
            last_used=datetime.now(),
            expires_at=datetime.now()
        )

        await self.__save_session(session)
        return session

    async def get_session(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        return await self.__get_session(user_id, session_uuid)

    async def get_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        return await self.__scan_for_user_sessions(user_id)

    async def rotate_session_tokens(self, session: AuthSessionInternal) -> None:
        session.access_token = create_access_token(session.user_id, session.session_uuid)
        session.refresh_token = create_refresh_token(session.user_id, session.session_uuid)
        session.expires_at = calculate_refresh_expire_at()
        await self.update_session(session)

    async def rotate_session_tokens_by_id(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        if (session := await self.get_session(user_id, session_uuid)) is None:
            return None

        await self.rotate_session_tokens(session)
        return session

    async def revoke_session_by_id(self, user_id: int, session_uuid: UUIDString) -> bool:
        return await self.__delete_session(user_id, session_uuid, soft=True)

    async def revoke_other_sessions(self, user_id: int, keep_session_uuid: UUIDString) -> None:
        for session in await self.get_user_sessions(user_id):
            if session.session_uuid == keep_session_uuid:
                continue

            await self.__delete_session(user_id, session.session_uuid, soft=True)

    async def update_session(self, updated_schema: AuthSessionInternal) -> None:
        await self.__save_session(updated_schema)

    async def session_heartbeat(self, session: AuthSessionInternal) -> None:
        session.last_used = datetime.now()
        await self.update_session(session)

    async def session_heartbeat_by_id(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        if (session := await self.get_session(user_id, session_uuid)) is None:
            return None

        await self.session_heartbeat(session)
        return session

    async def cleanup(self) -> None:  # TODO
        pass
