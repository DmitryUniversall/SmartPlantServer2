from starlette.requests import Request

from src.app.main.components.auth.models.auth_session import AuthSessionPrivate
from src.app.main.components.auth.models.user import UserPrivate
from src.app.main.components.auth.repository import AuthRepositoryST
from src.app.main.exceptions import ForbiddenHTTPException
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import RegisterReqeustPayload, RegisterResponsePayload
from ..router import auth_router

_auth_repository = AuthRepositoryST()


@auth_router.post("/register/")
async def register_route(payload: RegisterReqeustPayload, request: Request) -> ApplicationJsonResponse:
    if request.client is None:
        raise ForbiddenHTTPException(message="Client is unknown")

    auth_info = await _auth_repository.register(
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent", "unknown"),
        **payload.model_dump()
    )

    return SuccessResponse[RegisterResponsePayload](
        data=RegisterResponsePayload(
            user=auth_info.user.convert_to(UserPrivate),
            session=auth_info.session.convert_to(AuthSessionPrivate),
            access_token=auth_info.session.access_token,
            refresh_token=auth_info.session.refresh_token
        )
    )
