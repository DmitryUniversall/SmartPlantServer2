from fastapi import Depends

from src.app.main.components.auth.models.auth_info import AuthInfo
from src.app.main.components.auth.models.user import UserPrivate
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import GetMeResponsePayload
from ..router import auth_router

_jwt_auth = HTTPJWTBearerAuthDependency()


@auth_router.get("/users/me/")
async def get_me_route(auth_info: AuthInfo = Depends(_jwt_auth)) -> ApplicationJsonResponse:
    return SuccessResponse[GetMeResponsePayload](
        data=GetMeResponsePayload(
            user=auth_info.user.convert_to(UserPrivate)
        )
    )
