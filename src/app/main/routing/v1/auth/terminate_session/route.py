from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.services.auth_service import AuthServiceST
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from src.core.utils.types import UUIDString
from ..router import auth_router

_auth_service = AuthServiceST()
_jwt_auth = HTTPJWTBearerAuthDependency()


@auth_router.post("/sessions/{session_uuid}/terminate/")
async def terminate_session_route(
        session_uuid: UUIDString,
        auth_info: AuthInfo = Depends(_jwt_auth)
) -> ApplicationJsonResponse:
    await _auth_service.revoke_session(user_id=auth_info.user.id, session_uuid=session_uuid)

    return SuccessResponse[None]()
