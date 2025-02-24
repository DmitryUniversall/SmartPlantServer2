from starlette.requests import Request

from src.app.main.components.auth.entities.auth_session import AuthSessionPrivate
from src.app.main.components.auth.entities.user import UserPrivate
from src.app.main.components.auth.services.auth_service import AuthServiceST
from src.app.main.exceptions import ForbiddenHTTPException
from src.app.main.http import ApplicationJsonResponse, CreatedResponse
from .schemas import RegisterReqeustPayload, RegisterResponsePayload
from ..router import auth_router

_auth_service = AuthServiceST()


@auth_router.post("/register/")
async def register_route(request: Request, payload: RegisterReqeustPayload) -> ApplicationJsonResponse:
    if request.client is None:
        raise ForbiddenHTTPException(message="Client is unknown")

    auth_info = await _auth_service.register(
        ip_address=request.client.host,
        user_agent=request.headers.get("User-Agent", "unknown"),
        **payload.model_dump()
    )

    return CreatedResponse[RegisterResponsePayload](
        data=RegisterResponsePayload(
            user=auth_info.user.convert_to(UserPrivate),
            session=auth_info.session.convert_to(AuthSessionPrivate),
            access_token=auth_info.session.access_token,
            refresh_token=auth_info.session.refresh_token
        )
    )
