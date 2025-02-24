from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageServiceST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import RequestPayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_service = StorageServiceST()


@storage_router.post("/direct/response/")
async def direct_response_route(
        payload: RequestPayload,
        auth_info: AuthInfo = Depends(_jwt_auth),
) -> ApplicationJsonResponse:
    await _storage_service.send_response(
        user_id=auth_info.user.id,
        response_to_message_uuid=payload.response_to_message_uuid,
        **payload.message.to_json_dict(),
    )

    return SuccessResponse[None]()
