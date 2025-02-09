import json
import logging
from typing import AsyncGenerator, Type

from src.app.bases.db import BaseSchema
from src.app.main.redis.redis_client_mixin import RedisClientMixin
from src.core.utils.types import JsonDict

_logger = logging.getLogger(__name__)


class RedisQueue[schemaT: BaseSchema](RedisClientMixin):
    def __init__(
            self,
            schema_cls: Type[schemaT],
            key: str,
            max_size: int = 5000,
            overflow_buffer: int = 100,
            **kwargs
    ) -> None:
        super().__init__(**kwargs)

        self._schema_cls: Type[schemaT] = schema_cls
        self._overflow_buffer: int = overflow_buffer
        self._max_size: int = max_size
        self._key: str = key

    async def _write_data(self, data: str) -> None:
        redis = await self.get_redis()

        new_size = await redis.rpush(self._key, data)  # type: ignore
        if new_size > self._max_size:
            await redis.ltrim(self._key, self._max_size - self._overflow_buffer, -1)  # type: ignore

    async def _write_json(self, data: JsonDict) -> None:
        await self._write_data(json.dumps(data))

    async def _data_stream(self, *, timeout: int = 0) -> AsyncGenerator[str | None, None]:
        redis = await self.get_redis()

        while True:
            data = await redis.blpop([self._key], timeout=timeout)  # type: ignore
            yield None if data is None else data[1]

    async def _json_stream(self, **kwargs) -> AsyncGenerator[JsonDict | None, None]:
        async for data in self._data_stream(**kwargs):  # type: ignore
            yield None if data is None else json.loads(data)

    async def write(self, schema: schemaT, **kwargs) -> None:
        if not isinstance(schema, self._schema_cls):
            raise TypeError(f"{self.__class__.__name__} can only contain objects of type {self._schema_cls.__name__}")

        await self._write_data(schema.model_dump_json(**kwargs))

    async def stream(self, **kwargs) -> AsyncGenerator[schemaT | None, None]:
        async for data in self._json_stream(**kwargs):
            yield None if data is None else self._schema_cls.model_validate(data)

    async def wait(self, **kwargs) -> schemaT | None:
        async for item in self.stream(**kwargs):
            return item

    async def size(self) -> int:
        redis = await self.get_redis()
        return await redis.llen(self._key)  # type: ignore

    async def clear(self) -> None:
        redis = await self.get_redis()
        await redis.delete(self._key)  # type: ignore

    async def peek(self, index: int = 0) -> schemaT | None:
        redis = await self.get_redis()
        if (data := await redis.lindex(self._key, index)) is None:  # type: ignore
            return None

        json_data = json.loads(data)
        return self._schema_cls.model_validate(json_data)

    async def drain(self) -> list[schemaT]:
        redis = await self.get_redis()

        items: list[schemaT] = []
        while True:
            if (data := await redis.lpop(self._key)) is None:  # type: ignore
                break

            json_data = json.loads(data)
            items.append(self._schema_cls.model_validate(json_data))
        return items
