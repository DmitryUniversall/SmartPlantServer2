from starlette.requests import Request

from src.app.main.components.auth.models.auth_session import AuthSessionPrivate
from src.app.main.components.auth.models.user import UserPrivate
from src.app.main.components.auth.repository import AuthRepositoryST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import LoginRequestPayload, LoginResponsePayload
from ..router import auth_router

_auth_repository = AuthRepositoryST()


@auth_router.post("/login/")
async def login_route(payload: LoginRequestPayload, request: Request) -> ApplicationJsonResponse:
    assert request.client is not None  # TODO: raise HttpException

    auth_info = await _auth_repository.login(
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
