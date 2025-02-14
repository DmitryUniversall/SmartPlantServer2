from typing import Unpack

from src.app.main.components.storage.internal_utils import AbstractStorageManager, RedisCachedStorageManager
from src.app.main.components.storage.models import StorageDirectRequest, StorageDirectResponse, StorageDirectMessage
from src.app.main.components.storage.models.channel_message.schema import StorageChannelMessage
from src.app.main.components.storage.models.channel_message.types import StorageDirectMessageCreateTD, StorageChannelMessageCreateTD
from src.core.utils.singleton import SingletonMeta


class StorageRepositoryST(metaclass=SingletonMeta):
    def __init__(self):
        self._storage_manager: AbstractStorageManager = RedisCachedStorageManager()

    async def send_request(
            self,
            ttl: int,
            **message_data: Unpack[StorageDirectMessageCreateTD]
    ) -> StorageDirectResponse | None:
        message = StorageDirectRequest(**message_data)

        return await self._storage_manager.send_direct_request(message, ttl=ttl)

    async def send_response(
            self,
            response_to_message_uuid: str,
            ttl: int | None = None,
            **message_data: Unpack[StorageDirectMessageCreateTD]
    ) -> None:
        message = StorageDirectResponse(**message_data)

        return await self._storage_manager.send_direct_response(message, response_to_message_uuid=response_to_message_uuid, ttl=ttl)

    async def write_to_channel(self, **message_data: Unpack[StorageChannelMessageCreateTD]) -> StorageChannelMessage:
        return await self._storage_manager.write_to_channel(**message_data)

    async def listen_direct(self, user_id: int, device_name: str, limit: int, *, timeout: int) -> tuple[StorageDirectMessage, ...]:
        return await self._storage_manager.listen_direct(user_id, device_name, limit, timeout=timeout)

    async def listen_channel(self, user_id: int, channel_name: str, offset_id: int, limit: int, *, timeout: int) -> tuple[StorageChannelMessage, ...]:
        return await self._storage_manager.listen_channel(user_id, channel_name, offset_id, limit, timeout=timeout)
