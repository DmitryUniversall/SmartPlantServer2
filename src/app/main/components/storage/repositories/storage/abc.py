from abc import ABC, abstractmethod
from typing import Unpack

from src.app.main.components.storage.entities import (
    StorageDirectResponse,
    StorageDirectMessage,
    StorageChannelMessage,
    StorageChannelMessageCreateTD, StorageDirectRequest
)


class AbstractStorageRepository(ABC):
    @abstractmethod
    async def send_direct(self, message: StorageDirectMessage, *, ttl: int) -> None:
        ...

    @abstractmethod
    async def send_direct_request(self, request: StorageDirectRequest, *, ttl: int, wait: bool = True) -> StorageDirectResponse | None:
        ...

    @abstractmethod
    async def send_direct_response(self, response: StorageDirectResponse, response_to_message_uuid: str, *, ttl: int | None = None) -> None:
        ...

    @abstractmethod
    async def write_to_channel(self, **message_data: Unpack[StorageChannelMessageCreateTD]) -> StorageChannelMessage:
        ...

    @abstractmethod
    async def listen_channel(self, user_id: int, channel_name: str, offset_id: int, limit: int, *, timeout: int) -> tuple[StorageChannelMessage, ...]:
        ...

    @abstractmethod
    async def listen_direct(self, user_id: int, device_name: str, limit: int, *, timeout: int) -> tuple[StorageDirectMessage, ...]:
        ...
