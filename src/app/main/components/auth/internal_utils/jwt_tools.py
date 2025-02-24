from datetime import datetime, timedelta
from typing import Dict, Any, Union, TYPE_CHECKING

import jwt

from src.core.state import project_settings
from src.core.utils.types import JsonDict, UUIDString

if TYPE_CHECKING:
    from src.app.main.components.auth.entities.auth_token_payload.schemas import AccessTokenPayload, RefreshTokenPayload


def create_jwt_token(*, payload: JsonDict, exp: Union[int, float]) -> str:
    encoded_jwt = jwt.encode(
        payload={
            "exp": exp,
            **payload
        },
        key=project_settings.SECRET_KEY,
        algorithm=project_settings.TOKEN_ENCRYPTION_ALGORITHM
    )

    return encoded_jwt


def decode_jwt_token(token: str) -> Dict[str, Any]:
    return jwt.decode(
        jwt=token,
        key=project_settings.SECRET_KEY,
        algorithms=[project_settings.TOKEN_ENCRYPTION_ALGORITHM]
    )


def calculate_access_expire_at(start: datetime | None = None, ttl: int | None = None) -> datetime:
    start = start if start is not None else datetime.now()
    ttl = ttl if ttl is not None else project_settings.ACCESS_TOKEN_TTL
    return start + timedelta(seconds=ttl)


def calculate_refresh_expire_at(start: datetime | None = None, ttl: int | None = None) -> datetime:
    start = start if start is not None else datetime.now()
    ttl = ttl if ttl is not None else project_settings.REFRESH_TOKEN_TTL
    return start + timedelta(seconds=ttl)


def create_access_token_with_payload(payload: 'AccessTokenPayload') -> str:
    return create_jwt_token(payload=payload.to_json_dict(exclude='exp'), exp=payload.exp.timestamp())


def create_refresh_token_with_payload(payload: 'RefreshTokenPayload') -> str:
    return create_jwt_token(payload=payload.to_json_dict(exclude='exp'), exp=payload.exp.timestamp())


def create_access_token(user_id: int, session_uuid: UUIDString, token_uuid: str | None = None) -> str:
    from src.app.main.components.auth.entities.auth_token_payload.schemas import AccessTokenPayload

    payload = AccessTokenPayload(user_id=user_id, session_uuid=session_uuid, token_uuid=token_uuid)
    return create_access_token_with_payload(payload=payload)


def create_refresh_token(user_id: int, session_uuid: UUIDString, token_uuid: str | None = None) -> str:
    from src.app.main.components.auth.entities.auth_token_payload.schemas import RefreshTokenPayload

    payload = RefreshTokenPayload(user_id=user_id, session_uuid=session_uuid, token_uuid=token_uuid)
    return create_refresh_token_with_payload(payload=payload)
