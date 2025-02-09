import logging

from redis import asyncio as aioredis

from src.core.state import project_settings

_logger = logging.getLogger(__name__)


class RedisClientMixin:
    def __init__(self, db: int = 0) -> None:
        self._db: int = db
        self._redis: aioredis.client.Redis | None = None

    async def _create_redis(self) -> aioredis.client.Redis:
        return await aioredis.from_url(
            url=project_settings.REDIS_BASE_URL + f"{self._db}/",
            encoding=project_settings.REDIS_ENCODING,
            decode_responses=True
        )

    async def get_redis(self) -> aioredis.client.Redis:
        if self._redis is None:
            self._redis = await self._create_redis()

        return self._redis
