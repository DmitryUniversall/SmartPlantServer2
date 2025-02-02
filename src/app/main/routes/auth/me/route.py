from http import HTTPStatus

from fastapi import Depends

from src.app.main.components.auth.auth_info import AuthInfo
from src.app.main.components.auth.models.user import UserPrivate
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.http import ApplicationJsonResponse
from src.app.main.models_global import ApplicationResponsePayload
from src.core.state import project_settings
from .schemas import GetMeResponsePayload
from ..router import auth_router

_jwt_auth = HTTPJWTBearerAuthDependency()


@auth_router.get("/me/")
async def get_me_route(auth_info: AuthInfo = Depends(_jwt_auth)) -> ApplicationJsonResponse:
    return ApplicationJsonResponse(
        status_code=HTTPStatus.OK,
        content=ApplicationResponsePayload[GetMeResponsePayload](
            **project_settings.APPLICATION_STATUS_CODES.GENERICS.SUCCESS,
            data=GetMeResponsePayload(
                user=auth_info.user.convert_to(UserPrivate)
            )
        )
    )
