import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from http import HTTPStatus

import jwt

from src.app.main.components.auth.exceptions import TokenExpiredHTTPException, TokenInvalidHTTPException
from src.app.main.components.auth.internal_utils.jwt_tools import decode_jwt_token
from src.app.main.components.auth.models.auth_session import AuthSessionInternal
from src.core.utils.types import UUIDString, JsonDict


class AbstractSessionManager(ABC):
    @abstractmethod
    async def create_session(
            self,
            user_id: int,
            ip_address: str,
            user_agent: str,
            session_name: str,
            access_token_expires_at: datetime | None = None,
            refresh_token_expires_at: datetime | None = None
    ) -> AuthSessionInternal:
        """Create a new session with generated session ID"""

    @abstractmethod
    async def validate_access_token(self, access_token: str) -> AuthSessionInternal:
        """Validate access token and update last_used"""

    @abstractmethod
    async def validate_refresh_token(self, refresh_token: str) -> AuthSessionInternal:
        """Validate refresh token"""

    @abstractmethod
    async def get_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        """Get all active sessions for user"""

    @abstractmethod
    async def get_session(self, user_id: int, session_id: UUIDString) -> AuthSessionInternal:
        """Get specific session details"""

    @abstractmethod
    async def rotate_session_tokens(self, session: AuthSessionInternal) -> None:
        """Force token rotation for session"""

    @abstractmethod
    async def rotate_session_tokens_by_id(self, user_id: int, session_id: UUIDString) -> AuthSessionInternal:
        """Refresh session tokens by id"""

    @abstractmethod
    async def refresh_session(self, refresh_token: str) -> AuthSessionInternal:
        """Refresh session tokens by refresh token"""

    @abstractmethod
    async def revoke_session(self, user_id: int, session_id: UUIDString) -> None:
        """Revoke specific session"""

    @abstractmethod
    async def revoke_other_sessions(self, user_id: int, keep_session_id: UUIDString) -> None:
        """Revoke all sessions except specified one"""

    @abstractmethod
    async def update_session(self, updated_schema: AuthSessionInternal) -> None:
        """Update session metadata"""

    @abstractmethod
    async def session_heartbeat(self, session: AuthSessionInternal) -> None:
        """Update last_used timestamp"""

    @abstractmethod
    async def session_heartbeat_by_id(self, user_id: int, session_id: UUIDString) -> AuthSessionInternal:
        """Update last_used timestamp by id"""

    @abstractmethod
    async def generate_access_token(self, user_id: int, session_id: UUIDString, expires_at: datetime | None = None) -> str:
        """Generate new access token"""

    @abstractmethod
    async def generate_refresh_token(self, user_id: int, session_id: UUIDString, expires_at: datetime | None = None) -> str:
        """Generate new refresh token"""

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup expired sessions"""

    def decode_jwt_token(self, token: str) -> JsonDict:
        try:
            return decode_jwt_token(token)
        except jwt.ExpiredSignatureError as error:
            raise TokenExpiredHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error
        except jwt.PyJWTError as error:
            raise TokenInvalidHTTPException(status_code=HTTPStatus.UNAUTHORIZED) from error

    def generate_session_id(self) -> str:
        return str(uuid.uuid4())

    def generate_token_id(self) -> str:
        return str(uuid.uuid4())
