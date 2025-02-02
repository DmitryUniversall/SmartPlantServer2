from datetime import datetime
from http import HTTPStatus

from src.app.main.components.auth.auth_info import AuthInfo
from src.app.main.components.auth.exceptions import (
    AuthUserAlreadyExists,
    WrongAuthCredentialsHTTPException,
    SuspiciousActivityHTTPException
)
from src.app.main.components.auth.internal_utils.sessions import (
    AbstractSessionManager,
    RedisSessionManager
)
from src.app.main.components.auth.models.auth_session import AuthSessionInternal
from src.app.main.components.auth.models.user.model import UserModel
from src.app.main.components.auth.models.user.schemas import UserInternal
from src.app.main.components.auth.models.user.user_resource import UserResourceST
from src.app.main.db.exceptions import UniqueConstraintFailed
from src.core.utils.singleton import SingletonMeta
from src.core.utils.types import UUIDString


class AuthenticatorST(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._session_manager: AbstractSessionManager = RedisSessionManager()
        self._user_resource: UserResourceST = UserResourceST()

    async def _log_security_event(self) -> None:  # TODO
        pass

    async def _invalidate_session(self, user_id: int, session_id: UUIDString) -> None:
        await self._session_manager.revoke_session(user_id, session_id)

    async def _handle_suspicious_activity(self, user: UserInternal, session: AuthSessionInternal) -> None:
        await self._log_security_event()
        await self._invalidate_session(user.id, session.session_id)

    async def _register_user(self, username: str, password: str, **field) -> UserInternal:
        try:
            user_model = await self._user_resource.create_user(username, password, **field)
            return user_model.to_schema(scheme_cls=UserInternal)
        except UniqueConstraintFailed as error:
            raise AuthUserAlreadyExists(status_code=HTTPStatus.CONFLICT) from error

    async def _login_user(self, username: str, password: str, **fields) -> UserInternal:
        try:
            user_model = await self._user_resource.get_by_credentials(username=username, password=password, **fields)
            return user_model.to_schema(scheme_cls=UserInternal)
        except UserModel.DoesNotExist as error:
            raise WrongAuthCredentialsHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error

    async def authenticate(self, access_token: str) -> AuthInfo:
        session = await self._session_manager.validate_access_token(access_token)
        user_model = await self._user_resource.get_by_pk(session.user_id)
        return AuthInfo(user=user_model.to_schema(UserInternal), session=session)

    async def refresh(self, refresh_token: str, current_client_ip: str, current_client_user_agent: str) -> AuthInfo:
        session = await self._session_manager.refresh_session(refresh_token)
        user_model = await self._user_resource.get_by_pk(session.user_id)
        user_schema = user_model.to_schema(UserInternal)

        if session.ip_address != current_client_ip or session.user_agent != current_client_user_agent:
            await self._handle_suspicious_activity(user_schema, session)
            raise SuspiciousActivityHTTPException(status_code=HTTPStatus.FORBIDDEN)

        return AuthInfo(user=user_schema, session=session)

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
        user = await self._register_user(username, password, **user_fields)
        session = await self._session_manager.create_session(
            user.id, ip_address, user_agent, session_name,
            access_token_expires_at, refresh_token_expires_at
        )

        return AuthInfo(user=user, session=session)

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
        user = await self._login_user(username, password, **user_fields)
        session = await self._session_manager.create_session(
            user.id, ip_address, user_agent, session_name,
            access_token_expires_at, refresh_token_expires_at
        )

        return AuthInfo(user=user, session=session)

    async def revoke_session(self, user_id: int, session_id: UUIDString) -> None:
        await self._session_manager.revoke_session(user_id, session_id)
