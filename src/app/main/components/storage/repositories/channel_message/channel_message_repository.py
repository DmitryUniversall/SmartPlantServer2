from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.bases.repositories import ObservableRepository
from src.app.main.components.storage.entities.channel_message import StorageChannelMessage, StorageChannelMessageModel
from src.app.main.db import AsyncDatabaseManagerST
from src.core.utils.singleton import ABCSingletonMeta


class StorageChannelMessageRepositoryST(ObservableRepository[StorageChannelMessageModel, int], metaclass=ABCSingletonMeta):
    __model_cls__: type[StorageChannelMessageModel] = StorageChannelMessageModel
    __db_manager__: AsyncDatabaseManagerST = AsyncDatabaseManagerST()

    async def _fetch_messages(
            self,
            session: AsyncSession,
            user_id: int,
            channel_name: str,
            offset_id: int,
            limit: int
    ) -> Sequence[StorageChannelMessageModel]:
        stmt = (
            select(StorageChannelMessageModel)
            .where(
                StorageChannelMessageModel.user_id == user_id,  # type: ignore
                StorageChannelMessageModel.channel_name == channel_name,  # type: ignore
                self._model_pk_field > offset_id
            )
            .order_by(StorageChannelMessageModel.id)
            .limit(limit)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def get_messages(
            self,
            user_id: int,
            channel_name: str,
            offset_id: int,
            limit: int
    ) -> tuple[StorageChannelMessage, ...]:
        async with self.__db_manager__.session() as session:
            messages = await self._fetch_messages(session, user_id, channel_name, offset_id, limit)
            return tuple(map(lambda x: x.to_schema(StorageChannelMessage), messages))  # type: ignore
