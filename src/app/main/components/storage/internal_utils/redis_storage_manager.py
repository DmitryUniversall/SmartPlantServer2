import logging
from typing import Unpack

from src.app.main.components.storage.internal_utils.storage_manager import AbstractStorageManager
from src.app.main.components.storage.models import (
    StorageDirectResponse,
    StorageDirectMessage,
    StorageDirectRequest,
    StorageDirectMessageIntent,
    StorageChannelMessageResourceST,
    StorageChannelMessageModel,
    StorageChannelMessageCreateTD
)
from src.app.main.components.storage.models.channel_message import StorageChannelMessage
from src.app.main.redis import RedisClientMixin
from src.core.exceptions import IllegalArgumentError
from src.core.state import project_settings
from src.core.utils.types import UUIDString

_logger = logging.getLogger(__name__)


class RedisCachedStorageManager(RedisClientMixin, AbstractStorageManager):
    def __init__(self) -> None:
        super().__init__(db=project_settings.STORAGE_REDIS_DB_ID)

        self._scm_resource = StorageChannelMessageResourceST()

    def _get_user_storage_key(self, user_id: int) -> str:
        return f"storage:{user_id}"

    def _get_channel_key(self, user_id: int, channel_name: str) -> str:
        return self._get_user_storage_key(user_id) + f":channel:{channel_name}"

    def _get_channel_meta_key(self, user_id: int, channel_name: str) -> str:
        return self._get_channel_key(user_id, channel_name) + ":__meta__"

    def _get_channel_stream_key(self, user_id: int, channel_name: str) -> str:
        return self._get_channel_key(user_id, channel_name) + ":__stream__"

    def _get_direct_key(self, user_id: int, target_name: str) -> str:
        return self._get_user_storage_key(user_id) + f":direct:{target_name}"

    def _get_response_direct_key(self, user_id: int, sender_name: str, response_to_message_uuid: str) -> str:
        return self._get_direct_key(user_id, sender_name) + f":response:{response_to_message_uuid}"

    async def _wait_for_direct_response(self, request: StorageDirectRequest, *, timeout: int) -> StorageDirectResponse | None:
        redis = await self.get_redis()
        key = self._get_response_direct_key(request.user_id, request.target_name, request.uuid)

        if (result := await redis.blpop([key], timeout=timeout)) is None:
            return None

        return StorageDirectResponse.model_validate_json(result[1])

    async def _send_direct(self, message: StorageDirectMessage, *, key: str | None = None, ttl: int | None = None) -> None:
        redis = await self.get_redis()
        key = key if key is not None else self._get_direct_key(message.user_id, message.target_name)
        await redis.rpush(key, message.model_dump_json())

        if ttl is not None:
            await redis.expire(key, time=ttl)  # FIXME: This will delete whole list, not just this message

    async def _send_direct_request(self, request: StorageDirectRequest, *, ttl: int, wait: bool = True) -> StorageDirectResponse | None:
        _logger.debug(f"Sending direct request {request.uuid} ({request.sender_name} -> {request.target_name})")

        await self._send_direct(request, ttl=ttl)
        return await self._wait_for_direct_response(request, timeout=ttl) if wait else None

    async def _send_direct_response(self, response: StorageDirectResponse, response_to_message_uuid: UUIDString, ttl: int | None = None) -> None:
        _logger.debug(f"Sending direct response to {response_to_message_uuid} ({response.sender_name} -> {response.target_name})")

        key = self._get_response_direct_key(response.user_id, response.sender_name, response_to_message_uuid)
        await self._send_direct(response, key=key, ttl=ttl)  # Use TTL with response is safe because each response has its own key

    async def _listen_direct(self, user_id: int, device_name: str, limit: int, timeout: int) -> tuple[StorageDirectMessage, ...]:
        redis = await self.get_redis()
        key = self._get_direct_key(user_id, device_name)

        if (first := await redis.blpop([key], timeout=timeout)) is None:
            return tuple()

        messages = [first[1]] + await redis.lrange(key, 0, limit)  # TODO: Check if limit is working as planned

        await redis.delete(key)
        return tuple(map(StorageDirectMessage.model_validate_json, messages))

    async def _write_to_channel(self, **message_data: Unpack[StorageChannelMessageCreateTD]) -> StorageChannelMessage:
        # Save to db
        model = StorageChannelMessageModel(**message_data)
        await self._scm_resource.create(model)
        message = model.to_schema(StorageChannelMessage)

        # Add to redis stream
        redis = await self.get_redis()
        key = self._get_channel_stream_key(message.user_id, message.channel_name)

        await redis.xadd(
            name=key,
            fields={"data": message.model_dump_json()},  # TODO: Should I create new dict here?
            id=f"{message.id}-0",
            maxlen=project_settings.STORAGE_CHANNEL_CACHE_SIZE,
            approximate=True
        )

        return message

    async def _wait_for_message_in_redis(self, user_id: int, channel_name: str, timeout: int) -> tuple[StorageChannelMessage, ...]:
        _logger.debug(f"Waiting for messages in channel {user_id}:{channel_name}")

        redis = await self.get_redis()
        key = self._get_channel_stream_key(user_id, channel_name)

        # Using '$' means we only want messages that arrive after this call
        if not (response := await redis.xread({key: '$'}, block=timeout * 1000)):
            return tuple()

        messages: list[StorageChannelMessage] = []

        for stream_name, stream_messages in response:
            for message_id, message_data in stream_messages:
                messages.append(StorageChannelMessage.model_validate_json(message_data["data"]))

        return tuple(messages)

    async def _fetch_messages_from_redis(self, user_id: int, channel_name: str, offset_id: int, limit: int) -> tuple[StorageChannelMessage, ...]:
        _logger.debug(f"Fetching messages from redis stream for channel {user_id}:{channel_name}, offset_id={offset_id}")

        redis = await self.get_redis()
        key = self._get_channel_stream_key(user_id, channel_name)

        messages = await redis.xrange(key, min=f"{offset_id + 1}-0", max="+", count=limit)  # offset_id + 1 for not to return message that user already had seen
        return tuple(StorageChannelMessage.model_validate_json(message[1]["data"]) for message in messages)

    async def _fetch_messages_from_db(self, user_id: int, channel_name: str, offset_id: int, limit: int) -> tuple[StorageChannelMessage, ...]:
        _logger.debug(f"Fetching messages from db for channel {user_id}:{channel_name}, offset_id={offset_id}")

        return await self._scm_resource.get_messages(user_id, channel_name, offset_id, limit)

    async def _get_redis_stream_info(self, user_id: int, channel_name: str) -> tuple[int, int]:
        redis = await self.get_redis()
        key = self._get_channel_stream_key(user_id, channel_name)

        info = await redis.xinfo_stream(key)
        first_entry = info.get("first-entry")
        last_entry = info.get("last-entry")

        # If the stream is empty, these entries will be empty or None.
        if not first_entry or not last_entry:
            return -1, -1

        first_id = first_entry[0]
        last_id = last_entry[0]
        return int(first_id.split("-")[0]), int(last_id.split("-")[0])

    async def _listen_channel(self, user_id: int, channel_name: str, offset_id: int, limit: int, timeout: int) -> tuple[StorageChannelMessage, ...]:
        bottom_message_id, top_message_id = await self._get_redis_stream_info(user_id, channel_name)

        # Stream has no messages, wait for new ones
        if top_message_id == -1:
            return await self._wait_for_message_in_redis(user_id, channel_name, timeout)

        # User requested messages that are no longer in the Redis stream (expired)
        if offset_id < bottom_message_id:
            return await self._fetch_messages_from_db(user_id, channel_name, offset_id, limit)

        # User requested a message that does not exist yet (future message)
        if top_message_id <= offset_id:
            return await self._wait_for_message_in_redis(user_id, channel_name, timeout)

        # Requested messages exist in Redis
        return await self._fetch_messages_from_redis(user_id, channel_name, offset_id, limit)

    async def send_direct(self, message: StorageDirectMessage, *, ttl: int | None = None) -> None:
        if message.intent in (StorageDirectMessageIntent.REQUEST, StorageDirectMessageIntent.RESPONSE):
            raise IllegalArgumentError(f"Unable to send direct message with intent: {message.intent}; Use `send_direct_request` and `send_direct_response` instead")
        await self._send_direct(message, ttl=ttl)

    async def send_direct_request(self, request: StorageDirectRequest, *, ttl: int | None, wait: bool = True) -> StorageDirectResponse | None:
        return await self._send_direct_request(request, ttl=ttl, wait=wait)

    async def send_direct_response(self, response: StorageDirectResponse, response_to_message_uuid: UUIDString, *, ttl: int | None = None) -> None:
        await self._send_direct_response(response, response_to_message_uuid, ttl)

    async def listen_direct(self, user_id: int, device_name: str, limit: int, *, timeout: int) -> tuple[StorageDirectMessage, ...]:
        return await self._listen_direct(user_id, device_name, limit, timeout)

    async def write_to_channel(self, **message_data: Unpack[StorageChannelMessageCreateTD]) -> StorageChannelMessage:
        return await self._write_to_channel(**message_data)

    async def listen_channel(self, user_id: int, channel_name: str, offset_id: int, limit: int, *, timeout: int) -> tuple[StorageChannelMessage, ...]:
        return await self._listen_channel(user_id, channel_name, offset_id, limit, timeout)
