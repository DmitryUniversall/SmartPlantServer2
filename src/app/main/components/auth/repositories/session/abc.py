import uuid
from abc import ABC, abstractmethod

from src.app.main.components.auth.entities.auth_session import AuthSessionInternal
from src.core.utils.types import UUIDString


class AbstractSessionRepository(ABC):
    @abstractmethod
    async def create_session(self, user_id: int, ip_address: str, user_agent: str, session_name: str) -> AuthSessionInternal:
        """Create a new session with generated session ID"""

    @abstractmethod
    async def get_session(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        """Get specific session details"""

    @abstractmethod
    async def get_user_sessions(self, user_id: int) -> tuple[AuthSessionInternal, ...]:
        """Get all active sessions for user"""

    @abstractmethod
    async def rotate_session_tokens(self, session: AuthSessionInternal) -> None:
        """Force token rotation for session"""

    @abstractmethod
    async def rotate_session_tokens_by_id(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        """Refresh session tokens by id"""

    @abstractmethod
    async def revoke_session_by_id(self, user_id: int, session_uuid: UUIDString) -> bool:
        """Revoke specific session"""

    @abstractmethod
    async def revoke_other_sessions(self, user_id: int, keep_session_uuid: UUIDString) -> None:
        """Revoke all sessions except specified one"""

    @abstractmethod
    async def update_session(self, updated_schema: AuthSessionInternal) -> None:
        """Update session metadata"""

    @abstractmethod
    async def session_heartbeat(self, session: AuthSessionInternal) -> None:
        """Update last_used timestamp"""

    @abstractmethod
    async def session_heartbeat_by_id(self, user_id: int, session_uuid: UUIDString) -> AuthSessionInternal | None:
        """Update last_used timestamp by id"""

    @abstractmethod
    async def cleanup(self) -> None:
        """Cleanup expired sessions"""

    def generate_session_uuid(self) -> str:
        return str(uuid.uuid4())

    def generate_token_id(self) -> str:
        return str(uuid.uuid4())
