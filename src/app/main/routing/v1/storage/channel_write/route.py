from fastapi import Depends

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageRepositoryST
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from .schemas import WriteToChannelRequestPayload, WriteToChannelResponsePayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_repository = StorageRepositoryST()


@storage_router.post("/channel/{channel_name}/write/")
async def channel_write_route(
        channel_name: str,
        payload: WriteToChannelRequestPayload,
        auth_info: AuthInfo = Depends(_jwt_auth)
) -> ApplicationJsonResponse:
    message = await _storage_repository.write_to_channel(
        user_id=auth_info.user.id,
        channel_name=channel_name,
        **payload.message.to_json_dict()
    )

    return SuccessResponse[WriteToChannelResponsePayload](
        data=WriteToChannelResponsePayload(
            message=message
        )
    )
