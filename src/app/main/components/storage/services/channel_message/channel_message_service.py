from src.app.main.components.storage.entities import StorageChannelMessage, StorageChannelMessageModel
from src.app.main.components.storage.repositories.channel_message.channel_message_repository import StorageChannelMessageRepositoryST
from src.core.utils.singleton import SingletonMeta


class StorageChannelMessageServiceST(metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._channel_message_repository = StorageChannelMessageRepositoryST()

    async def get_messages(self, user_id: int, channel_name: str, offset_id: int, limit: int) -> tuple[StorageChannelMessage, ...]:
        return await self._channel_message_repository.get_messages(user_id, channel_name, offset_id, limit)

    async def create(self, message: StorageChannelMessageModel) -> None:
        await self._channel_message_repository.create(message)
