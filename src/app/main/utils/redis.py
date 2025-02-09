import asyncio
from contextlib import asynccontextmanager
from typing import Any, Sequence

from redis import asyncio as aioredis


def convert_for_redis[_KT](mapping: dict[_KT, Any]) -> dict[_KT, Any]:
    """
    Convert values in a mapping to types acceptable for Redis storage.

    :param mapping: `dict[_KT, Any]`
        A dictionary mapping keys to values that are to be stored in Redis.
        The function converts boolean values to integers to ensure compatibility.

    :return: `dict[_KT, Any]`
        A new dictionary with all boolean values converted to integers for Redis compatibility.
    """

    return {key: int(value) if isinstance(value, bool) else value for key, value in mapping.items()}


@asynccontextmanager
async def unsubscribe_after(pubsub: aioredis.client.PubSub):
    try:
        yield
    finally:
        await pubsub.unsubscribe()


async def listen_channels_realtime(redis_client: aioredis.client.Redis, channels: Sequence[str]) -> Any:
    pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(*channels)

    async with unsubscribe_after(pubsub):
        async for message in pubsub.listen():
            yield message


async def subscribe_for_message_realtime(redis_client: aioredis.client.Redis, channel: str, *, timeout: int | None) -> Any:
    async with asyncio.timeout(timeout):
        async for message in listen_channels_realtime(redis_client, (channel,)):
            return message


async def subscribe_for_message_realtime_safe(redis_client: aioredis.client.Redis, channel: str, *, timeout: int | None) -> Any | None:
    try:
        return await subscribe_for_message_realtime(redis_client, channel, timeout=timeout)
    except asyncio.TimeoutError:
        return None
