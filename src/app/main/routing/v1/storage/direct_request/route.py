from fastapi import Depends
from starlette.requests import Request

from src.app.bases.http.connection import cancel_on_disconnect
from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageServiceST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import ResponsePayload, RequestPayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_service = StorageServiceST()


@storage_router.post("/direct/request/")
async def direct_request_route(
        payload: RequestPayload,
        request: Request,
        auth_info: AuthInfo = Depends(_jwt_auth),
) -> ApplicationJsonResponse:
    async with cancel_on_disconnect(request):
        response = await _storage_service.send_request(
            user_id=auth_info.user.id,
            ttl=payload.timeout,
            **payload.message.to_json_dict()
        )

    return SuccessResponse[ResponsePayload](
        data=ResponsePayload(
            responded=response is not None,
            response=response
        )
    )
