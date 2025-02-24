from starlette.requests import Request

from src.app.main.components.auth.entities.auth_session import AuthSessionPrivate
from src.app.main.components.auth.entities.user import UserPrivate
from src.app.main.components.auth.services.auth_service import AuthServiceST
from src.app.main.exceptions import ForbiddenHTTPException
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import LoginRequestPayload, LoginResponsePayload
from ..router import auth_router

_auth_service = AuthServiceST()


@auth_router.post("/login/")
async def login_route(request: Request, payload: LoginRequestPayload) -> ApplicationJsonResponse:
    if request.client is None:
        raise ForbiddenHTTPException(message="Client is unknown")

    auth_info = await _auth_service.login(
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent", "unknown"),
        **payload.model_dump()
    )

    return SuccessResponse(
        data=LoginResponsePayload(
            user=auth_info.user.convert_to(UserPrivate),
            session=auth_info.session.convert_to(AuthSessionPrivate),
            access_token=auth_info.session.access_token,
            refresh_token=auth_info.session.refresh_token
        )
    )
