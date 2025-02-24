from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.services.auth_service import AuthServiceST
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from ..router import auth_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_auth_service = AuthServiceST()


@auth_router.get("/logout/")
async def logout_route(auth_info: AuthInfo = Depends(_jwt_auth)) -> ApplicationJsonResponse:
    await _auth_service.revoke_session(auth_info.user.id, auth_info.session.session_uuid)
    return SuccessResponse[None]()
