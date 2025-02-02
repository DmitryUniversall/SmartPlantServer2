from datetime import datetime, timedelta
from typing import Dict, Any, Union

import jwt

from src.core.state import project_settings
from src.core.utils.types import JsonDict


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
