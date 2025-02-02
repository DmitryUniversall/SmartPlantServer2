from abc import abstractmethod, ABC
from functools import cached_property
from typing import Any, Sequence

import sqlalchemy
from sqlalchemy import select, delete, update, Result
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.bases.db import BaseModel
from src.app.bases.db.manager import AbstractAsyncDatabaseManager


class BaseResource[_modelT: BaseModel, _pkT: Any](ABC):
    """
    Base class for managing database resources. Provides common CRUD operations.
    """

    @property
    @abstractmethod
    def __model_cls__(self) -> type[_modelT]:
        """
        Abstract property to define the model class for the resource

        :return: `type[_modelT]`
            The class of the model associated with the resource
        """

    @property
    @abstractmethod
    def __db_manager__(self) -> AbstractAsyncDatabaseManager:
        """
        Abstract property to define the db manager instance to be used by the resource

        :return: `type[_modelT]`
            The db manager instance to be used by the resource
        """

    @cached_property
    def _model_pk_field(self) -> sqlalchemy.Column:
        """
        Property that returns model primary key field based on `__pk_field__`

        :return: `sqlalchemy.Column`
            Model primary key field
        """

        return getattr(self.__model_cls__, self.__model_cls__.__pk_field__)

    async def _fetch_by(self, session: AsyncSession, fields: dict[str, Any]) -> Result[tuple[_modelT]]:
        """
        Fetches records from the database filtered by the given fields.

        :param session: `AsyncSession`
            The SQLAlchemy async session to execute the query.

        :param fields: `dict[str, Any]`
            (Optional) The fields used for filtering the query.
            At least one filter parameter must be provided.

        :return: `Result[tuple[_modelT]]`
            The result of the executed query.

        :raises:
            :raise ValueError: If no filter parameters are provided.
        """

        if not fields:
            raise ValueError("At least one filter parameter must be provided")

        result = await session.execute(select(self.__model_cls__).filter_by(**fields))
        return result

    async def _fetch_one_by(self, session: AsyncSession, fields: dict[str, Any]) -> _modelT | None:
        """
        Fetches a single record from the database filtered by the given fields.
        Performs db request

        :param session: `AsyncSession`
            The SQLAlchemy async session to execute the query.

        :param fields: `dict[str, Any]`
            (Optional) The fields used for filtering the query.
            At least one filter parameter must be provided.

        :return: `_modelT`
            The first matching record, or `None` if no record is found.

        :raises:
            :raise ValueError: If no filter parameters are provided.
        """

        result = await self._fetch_by(session, fields)
        return result.scalar_one_or_none()

    async def _fetch_many_by(self, session: AsyncSession, fields: dict[str, Any]) -> Sequence[_modelT]:
        """
        Fetches multiple records from the database filtered by the given fields.
        Performs db request

        :param session: `AsyncSession`
            The SQLAlchemy async session to execute the query.

        :param fields: `dict[str, Any]`
            (Optional) The fields used for filtering the query.
            At least one filter parameter must be provided.

        :return: `Sequence[_modelT]`
            A list of matching records, or an empty list if no records are found.

        :raises:
            :raise ValueError: If no filter parameters are provided.
        """

        result = await self._fetch_by(session, fields)
        return result.scalars().all()

    async def _fetch_by_pk(self, session: AsyncSession, pk: _pkT) -> _modelT:
        """
        Fetch a model object by its pk. Performs db request

        :param session: `AsyncSession`
            The database session to execute the query

        :param pk: `_pkT`
            The pk of the object to fetch

        :return: `_modelT`
            The fetched model object
        """

        result = await session.execute(
            select(self.__model_cls__)
            .filter(self._model_pk_field == pk)
        )

        if (fetched := result.scalar_one_or_none()) is None:
            raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with pk={pk}")

        return fetched

    async def _delete_by_pk(self, session: AsyncSession, pk: _pkT) -> _modelT:
        """
        Delete a model object by its pk. Performs db request

        :param session: `AsyncSession`
            The database session to execute the query

        :param pk: `_pkT`
            The pk of the object to delete

        :return: `_modelT`
            Deleted model object
        """

        result = await session.execute(
            delete(self.__model_cls__)
            .where(self._model_pk_field == pk)
            .returning(self.__model_cls__)
        )

        if (deleted := result.scalar_one_or_none()) is None:
            raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with pk={pk}")

        await session.commit()
        return deleted

    async def _update_by_pk(self, session: AsyncSession, pk: _pkT, **fields) -> _modelT:
        """
        Update a model object by its pk. Performs db request

        :param session: `AsyncSession`
            The database session to execute the query

        :param pk: `_pkT`
            The pk of the object to update

        :param fields: `dict[str, Any]`
            The fields to update with their new values

        :return: `_modelT`
            The updated model object
        """

        result = await session.execute(
            update(self.__model_cls__)
            .where(self._model_pk_field == pk)
            .values(**fields)
            .returning(self.__model_cls__)
        )

        if (updated := result.scalar_one_or_none()) is None:
            raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with pk={pk}")

        await session.commit()
        return updated

    async def _update_model(self, session: AsyncSession, model_obj: _modelT) -> None:
        """
        Updates an existing model instance in the database. Performs db request

        :param session: `AsyncSession`
            Database session used for updating.

        :param model_obj: `_modelT`
            The model instance to update.
        """

        await session.merge(model_obj)
        await session.commit()

    async def _create(self, session: AsyncSession, model_obj: _modelT) -> None:
        """
        Inserts a new model instance into the database. Performs db request

        :param session: `AsyncSession`
            Database session used for insertion.

        :param model_obj: `_modelT`
            The model instance to insert.
        """

        session.add(model_obj)
        await session.commit()

    async def create(self, model_obj: _modelT) -> None:
        """
        Save a model object to the database

        :param model_obj: `_modelT`
            The model object to save
        """

        async with self.__db_manager__.transaction() as session:
            await self._create(session, model_obj)

    async def get_by_pk(self, pk: _pkT) -> _modelT:
        """
        Retrieve a model object by its pk

        :param pk: `_pkT`
            The pk of the object to retrieve

        :return: `_modelT`
            The fetched model object
        """

        async with self.__db_manager__.transaction() as session:
            return await self._fetch_by_pk(session, pk)

    async def delete(self, model_obj: _modelT) -> None:
        """
        Delete a model object from the database

        :param model_obj: `_modelT`
            The model object to delete
        """

        async with self.__db_manager__.transaction() as session:
            await session.delete(model_obj)
            await session.commit()

    async def delete_by_pk(self, pk: _pkT) -> _modelT:
        """
        Delete a model object by its pk

        :param pk: `_pkT`
            The pk of the object to delete
        """

        async with self.__db_manager__.transaction() as session:
            return await self._delete_by_pk(session, pk)

    async def update(self, model_obj: _modelT, **fields) -> None:
        """
        Update a model object with the given fields

        :param model_obj: `_modelT`
            The model object to update

        :param fields: `dict[str, Any]`
            The fields to update with their new values
        """

        for key, value in fields.items():
            setattr(model_obj, key, value)

        async with self.__db_manager__.transaction() as session:
            await self._update_model(session, model_obj)

    async def update_by_pk(self, pk: _pkT, **fields) -> _modelT:
        """
        Update a model object by its pk with the given fields

        :param pk: `_pkT`
            The pk of the object to update

        :param fields: `dict[str, Any]`
            The fields to update with their new values

        :return: `_modelT`
            The updated model object
        """

        async with self.__db_manager__.transaction() as session:
            return await self._update_by_pk(session, pk, **fields)

    async def get_one_by(self, **fields) -> _modelT | None:
        """
        Fetches a single record from the database filtered by the given fields.

        :param fields: `dict[str, Any]`
            (Optional) The fields used for filtering the query.
            At least one filter parameter must be provided.

        :return: `_modelT`
            The first matching record, or `None` if no record is found.

        :raises:
            :raise ValueError: If no filter parameters are provided.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._fetch_one_by(session, fields)

    async def get_many_by(self, **fields) -> Sequence[_modelT]:
        """
        Fetches multiple records from the database filtered by the given fields.

        :param fields: `dict[str, Any]`
            (Optional) The fields used for filtering the query.
            At least one filter parameter must be provided.

        :return: `Sequence[_modelT]`
            A list of matching records, or an empty list if no records are found.

        :raises:
            :raise ValueError: If no filter parameters are provided.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._fetch_many_by(session, fields)
