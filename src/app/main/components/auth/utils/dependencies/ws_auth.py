import logging

from starlette.websockets import WebSocket

from src.app.main.components.auth.exceptions import AuthHTTPException
from src.app.main.components.auth.models.auth_info import AuthInfo
from src.app.main.components.auth.repository import AuthRepositoryST
from src.app.main.components.auth.utils.bearer_auth_mixin import BearerAuthMixin
from src.core.state import project_settings

_auth_repository = AuthRepositoryST()
_logger = logging.getLogger(__name__)


class WSJWTBearerAuthDependency(BearerAuthMixin):
    async def __call__(self, websocket: WebSocket) -> AuthInfo:
        authorization = websocket.headers.get("Authorization")

        try:
            access_token = await self.extract_token(authorization)
            return await _auth_repository.authenticate(access_token)
        except AuthHTTPException as error:
            await websocket.close(
                code=error.payload.application_status_code,
                reason=error.payload.message
            )
        except Exception as error:
            _logger.error(f"Unexpected error while authenticating user: {error}")
            await websocket.close(
                code=project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.INTERNAL_SERVER_ERROR.application_status_code,
                reason=project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.INTERNAL_SERVER_ERROR.message
            )
