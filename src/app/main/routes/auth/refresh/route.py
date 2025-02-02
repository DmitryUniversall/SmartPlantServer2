from starlette.requests import Request

from src.app.main.components.auth.repository import AuthRepositoryST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import RefreshRequestPayload, RefreshResponsePayload
from ..router import auth_router

_auth_repository = AuthRepositoryST()


@auth_router.post("/refresh/")
async def refresh_route(payload: RefreshRequestPayload, request: Request) -> ApplicationJsonResponse:
    assert request.client is not None  # TODO: raise HttpException

    auth_info = await _auth_repository.refresh(
        current_client_ip=request.client.host,
        current_client_user_agent=request.headers.get("User-Agent", "unknown"),
        refresh_token=payload.refresh_token
    )

    return SuccessResponse[RefreshResponsePayload](
        data=RefreshResponsePayload(
            access_token=auth_info.session.access_token,
            refresh_token=auth_info.session.refresh_token
        )
    )
