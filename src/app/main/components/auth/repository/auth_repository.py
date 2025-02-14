import logging
from datetime import datetime

from src.app.main.components.auth.internal_utils.authenticator import AuthenticatorST
from src.app.main.components.auth.models.auth_info import AuthInfo
from src.app.main.components.auth.models.user import UserInternal, UserResourceST
from src.core.utils.singleton import SingletonMeta
from src.core.utils.types import UUIDString

_logger = logging.getLogger(__name__)


class AuthRepositoryST(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._authenticator = AuthenticatorST()
        self._user_resource = UserResourceST()

    async def register(
            self,
            username: str,
            password: str,
            ip_address: str,
            user_agent: str,
            session_name: str,
            access_token_expires_at: datetime | None = None,
            refresh_token_expires_at: datetime | None = None,
            **user_fields
    ) -> AuthInfo:
        return await self._authenticator.register(
            username, password, ip_address, user_agent, session_name,
            access_token_expires_at, refresh_token_expires_at, **user_fields
        )

    async def login(
            self,
            username: str,
            password: str,
            ip_address: str,
            user_agent: str,
            session_name: str,
            access_token_expires_at: datetime | None = None,
            refresh_token_expires_at: datetime | None = None,
            **user_fields
    ) -> AuthInfo:
        return await self._authenticator.login(
            username, password, ip_address, user_agent, session_name,
            access_token_expires_at, refresh_token_expires_at, **user_fields
        )

    async def authenticate(self, access_token: str) -> AuthInfo:
        return await self._authenticator.authenticate(access_token)

    async def refresh(self, refresh_token: str, current_client_ip: str, current_client_user_agent: str) -> AuthInfo:
        return await self._authenticator.refresh(refresh_token, current_client_ip, current_client_user_agent)

    async def revoke_session(self, user_id: int, session_uuid: UUIDString) -> None:
        await self._authenticator.revoke_session(user_id, session_uuid)

    async def get_user_by_id(self, user_id: int) -> UserInternal:
        user_model = await self._user_resource.get_by_pk_strict(user_id)
        return user_model.to_schema(UserInternal)

    async def get_user_by_username(self, username: str, **fields) -> UserInternal:
        user_model = await self._user_resource.get_by_username(username, **fields)
        return user_model.to_schema(UserInternal)
