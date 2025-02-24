from starlette.requests import Request

from src.app.main.components.auth.entities.auth_info import AuthInfo
from src.app.main.components.auth.services.auth_service import AuthServiceST
from src.app.main.components.auth.utils.bearer_auth_mixin import BearerAuthMixin

_auth_service = AuthServiceST()


class HTTPJWTBearerAuthDependency(BearerAuthMixin):
    async def __call__(self, request: Request) -> AuthInfo:
        authorization = request.headers.get("Authorization")
        access_token = await self.extract_token(authorization)
        return await _auth_service.authenticate(access_token)
