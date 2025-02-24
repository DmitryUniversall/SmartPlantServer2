from starlette.requests import Request

from src.app.main.components.auth.services.auth_service import AuthServiceST
from src.app.main.exceptions import ForbiddenHTTPException
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import RefreshRequestPayload, RefreshResponsePayload
from ..router import auth_router

_auth_service = AuthServiceST()


@auth_router.post("/refresh/")
async def refresh_route(payload: RefreshRequestPayload, request: Request) -> ApplicationJsonResponse:
    if request.client is None:
        raise ForbiddenHTTPException(message="Client is unknown")

    auth_info = await _auth_service.refresh(
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
