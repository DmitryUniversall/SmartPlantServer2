from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageRepositoryST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import ListenDirectResponsePayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_repository = StorageRepositoryST()


@storage_router.get("/direct/{device_name}/listen/")
async def direct_listen_route(
        device_name: str,
        timeout: int = 60,
        limit: int = 10,
        auth_info: AuthInfo = Depends(_jwt_auth)
) -> ApplicationJsonResponse:
    messages = await _storage_repository.listen_direct(
        user_id=auth_info.user.id,
        device_name=device_name,
        timeout=timeout if timeout <= 60 else 60,
        limit=limit if limit <= 10 else 10,
    )

    return SuccessResponse[ListenDirectResponsePayload](
        data=ListenDirectResponsePayload(
            messages=messages
        )
    )
