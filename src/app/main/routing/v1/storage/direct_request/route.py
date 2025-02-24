from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageRepositoryST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import ResponsePayload, RequestPayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_repository = StorageRepositoryST()


@storage_router.post("/direct/request/")
async def direct_request_route(
        payload: RequestPayload,
        auth_info: AuthInfo = Depends(_jwt_auth),
) -> ApplicationJsonResponse:
    response = await _storage_repository.send_request(
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
