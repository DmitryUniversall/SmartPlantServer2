from http import HTTPStatus

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.entities.auth_session import AuthSessionInternal
from src.app.main.components.auth.entities.user.model import UserModel
from src.app.main.components.auth.entities.user.schemas import UserInternal
from src.app.main.components.auth.exceptions import (
    UserAlreadyExists,
    WrongAuthCredentialsHTTPException,
    SuspiciousActivityHTTPException,
    AuthUserUnknownHTTPException
)
from src.app.main.components.auth.services.session.session_service import SessionServiceST
from src.app.main.components.auth.services.user.user_service import UserServiceST
from src.app.main.db.exceptions import UniqueConstraintFailed
from src.core.utils.singleton import SingletonMeta
from src.core.utils.types import UUIDString


class AuthServiceST(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._session_service: SessionServiceST = SessionServiceST()
        self._user_service: UserServiceST = UserServiceST()

    async def _log_security_event(self) -> None:  # TODO
        pass

    async def _get_user_by_id(self, user_id: int) -> UserInternal:
        try:
            user_model = await self._user_service.get_user_by_id(user_id)
            return user_model.to_schema(UserInternal)
        except UserModel.DoesNotExist:
            raise AuthUserUnknownHTTPException()

    async def _revoke_session(self, user_id: int, session_uuid: UUIDString) -> None:
        await self._session_service.revoke_session(user_id, session_uuid)

    async def _handle_suspicious_activity(self, user: UserInternal, session: AuthSessionInternal) -> None:
        await self._log_security_event()
        await self._revoke_session(user.id, session.session_uuid)

    async def _register_user(self, username: str, password: str, **field) -> UserInternal:
        try:
            user_model = await self._user_service.create_user(username, password, **field)
            return user_model.to_schema(scheme_cls=UserInternal)
        except UniqueConstraintFailed as error:
            raise UserAlreadyExists(status_code=HTTPStatus.CONFLICT) from error

    async def _login_user(self, username: str, password: str, **fields) -> UserInternal:
        try:
            user_model = await self._user_service.get_by_auth_credentials(username=username, password=password, **fields)
            return user_model.to_schema(scheme_cls=UserInternal)
        except UserModel.DoesNotExist as error:
            raise WrongAuthCredentialsHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error

    async def authenticate(self, access_token: str) -> AuthInfo:
        session = await self._session_service.validate_access_token(access_token)
        user = await self._get_user_by_id(session.user_id)
        return AuthInfo(user=user, session=session)

    async def refresh(self, refresh_token: str, current_client_ip: str, current_client_user_agent: str) -> AuthInfo:
        session = await self._session_service.refresh_session(refresh_token)
        user = await self._get_user_by_id(session.user_id)

        if session.ip_address != current_client_ip or session.user_agent != current_client_user_agent:
            await self._handle_suspicious_activity(user, session)
            raise SuspiciousActivityHTTPException(status_code=HTTPStatus.FORBIDDEN)

        return AuthInfo(user=user, session=session)

    async def register(
            self,
            username: str,
            password: str,
            ip_address: str,
            user_agent: str,
            session_name: str,
            **user_fields
    ) -> AuthInfo:
        user = await self._register_user(username, password, **user_fields)
        session = await self._session_service.create_session(
            user.id, ip_address, user_agent, session_name
        )

        return AuthInfo(user=user, session=session)

    async def login(
            self,
            username: str,
            password: str,
            ip_address: str,
            user_agent: str,
            session_name: str,
            **user_fields
    ) -> AuthInfo:
        user = await self._login_user(username, password, **user_fields)
        session = await self._session_service.create_session(
            user.id, ip_address, user_agent, session_name
        )

        return AuthInfo(user=user, session=session)

    async def revoke_session(self, user_id: int, session_uuid: UUIDString) -> None:
        await self._session_service.revoke_session(user_id, session_uuid)
