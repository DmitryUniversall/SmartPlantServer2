from fastapi import Depends
from starlette.requests import Request

from src.app.bases.http.connection import cancel_on_disconnect
from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.utils.dependencies.http_auth import HTTPJWTBearerAuthDependency
from src.app.main.components.storage.services.storage_service import StorageServiceST
from src.app.main.exceptions import BadRequestHTTPException
from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from src.core.exceptions import ConcurrencyError
from .schemas import ListenDirectResponsePayload
from ..router import storage_router

_jwt_auth = HTTPJWTBearerAuthDependency()
_storage_service = StorageServiceST()


@storage_router.get("/direct/{device_name}/listen/")
async def direct_listen_route(
        device_name: str,
        request: Request,
        timeout: int = 60,
        limit: int = 10,
        auth_info: AuthInfo = Depends(_jwt_auth)
) -> ApplicationJsonResponse:
    async with cancel_on_disconnect(request):
        try:
            messages = await _storage_service.listen_direct(
                user_id=auth_info.user.id,
                device_name=device_name,
                timeout=timeout if timeout <= 60 else 60,
                limit=limit if limit <= 10 else 10,
            )
        except ConcurrencyError as error:
            raise BadRequestHTTPException(message=str(error))

    return SuccessResponse[ListenDirectResponsePayload](
        data=ListenDirectResponsePayload(
            messages=messages
        )
    )
