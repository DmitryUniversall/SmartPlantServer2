from fastapi import Depends

from src.app.main.components.auth.models.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.repository.storage_repository import StorageRepositoryST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import RequestPayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_repository = StorageRepositoryST()


@storage_router.post("/direct/response/")
async def direct_response_route(
        payload: RequestPayload,
        auth_info: AuthInfo = Depends(_jwt_auth),
) -> ApplicationJsonResponse:
    await _storage_repository.send_response(
        user_id=auth_info.user.id,
        **payload.message.to_json_dict(),
    )

    return SuccessResponse[None]()
