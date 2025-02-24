from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageServiceST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import ListenChannelResponsePayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_service = StorageServiceST()


@storage_router.get("/channel/{channel_name}/listen/")
async def channel_listen_route(
        channel_name: str,
        offset_id: int = 0,
        limit: int = 10,
        timeout: int = 60,
        auth_info: AuthInfo = Depends(_jwt_auth)
) -> ApplicationJsonResponse:
    messages = await _storage_service.listen_channel(
        user_id=auth_info.user.id,
        channel_name=channel_name,
        offset_id=offset_id if offset_id > 0 else 0,
        timeout=timeout if timeout <= 60 else 60,
        limit=limit if limit <= 20 else 20
    )

    return SuccessResponse[ListenChannelResponsePayload](
        data=ListenChannelResponsePayload(
            messages=messages
        )
    )
