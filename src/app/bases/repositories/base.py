from abc import ABC, abstractmethod
from functools import cached_property
from typing import Any, Sequence

import sqlalchemy
from sqlalchemy import select, update, delete, func, inspect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.strategy_options import _AbstractLoad

from src.app.bases.db import BaseModel, AbstractAsyncDatabaseManager
from .pagination import LazyPaginator, DBPaginateable


class BaseRepository[_modelT: BaseModel, _pkT: Any](DBPaginateable, ABC):
    """
    Base class for managing database entity.
    Provides common CRUD operations along with advanced filtering, ordering, relationship loading, bulk operations, and lazy pagination.
    """

    @property
    @abstractmethod
    def __model_cls__(self) -> type[_modelT]:
        """
        Return the model class for this repository.

        :return: `type[_modelT]`
            The model class associated with this repository.
        """

    @property
    @abstractmethod
    def __db_manager__(self) -> AbstractAsyncDatabaseManager:
        """
        Return the database manager instance used by this repository.

        :return: `AbstractAsyncDatabaseManager`
            The database manager for handling database operations.
        """

    @cached_property
    def _model_pk_field(self) -> sqlalchemy.Column:
        """
        Get the model's primary key field.

        :return: `sqlalchemy.Column`
            The primary key field of the model.
        """

        return getattr(self.__model_cls__, self.__model_cls__.__pk_field__)

    # ------------------------------------------------------
    # Helpers for Filtering, Ordering, and Relationship Loading
    # ------------------------------------------------------

    def _apply_filters(self, query, model: type[_modelT], filters: dict[str, Any]):  # TODO: Better typing
        """
        Apply filtering conditions to a query.
        Supports nested filters using double underscores (e.g., "user__first_name").

        :param query: `sqlalchemy.orm.Query`
            The SQLAlchemy query object to modify.

        :param model: `type[_modelT]`
            The model class for filtering.

        :param filters: `dict[str, Any]`
            Dictionary of filters to apply.

        :return: `sqlalchemy.orm.Query`
            The modified query object.
        """

        for key, value in filters.items():
            if "__" not in key:
                query = query.filter(getattr(model, key) == value)
                continue

            parts = key.split("__")
            current_model = model

            # For each part (except the last), join the related model.
            for part in parts[:-1]:
                query = query.join(getattr(current_model, part))
                current_model = getattr(current_model, part).property.mapper.class_

            # Filter on the final attribute.
            query = query.filter(getattr(current_model, parts[-1]) == value)

        return query

    def _apply_ordering(self, query, model: type[_modelT], order_by: Sequence[str]):
        """
        Apply ordering to a query.
        Each order string can be prefixed with "-" for descending order.

        :param query: `sqlalchemy.orm.Query`
            The SQLAlchemy query object to modify.

        :param model: `type[_modelT]`
            The model class for ordering.

        :param order_by: `Sequence[str]`
            List of fields to order by, with optional "-" prefix for descending order.

        :return: `sqlalchemy.orm.Query`
            The modified query object.
        """

        for order in order_by:
            if order.startswith("-"):
                column = getattr(model, order[1:])
                query = query.order_by(column.desc())
            else:
                column = getattr(model, order)
                query = query.order_by(column.asc())

        return query

    def _build_relationship_load_options(self, model: type[_modelT], depth: int) -> list[_AbstractLoad]:
        """
        Build eager-loading options for relationships up to the specified depth.

        :param model: `type[_modelT]`
            The model class whose relationships should be loaded.

        :param depth: `int`
            The depth of relationship loading.

        :return: `list[_AbstractLoad]`
            A list of SQLAlchemy load options.
        """

        if depth <= 0:
            return []

        opts: list[_AbstractLoad] = []
        mapper = inspect(model)

        for rel in mapper.relationships:
            opt = selectinload(getattr(model, rel.key))
            nested = self._build_relationship_load_options(rel.mapper.class_, depth - 1)
            if nested:
                opt = opt.options(*nested)
            opts.append(opt)

        return opts

    def _build_subquery_for_filters(self, filters: dict[str, Any]):
        """
        Build a subquery selecting primary keys matching the given filters.
        Used for UPDATE/DELETE operations that cannot use JOINs directly.

        :param filters: `dict[str, Any]`
            Dictionary of filters to apply.

        :return: `sqlalchemy.sql.Subquery`
            A subquery selecting the primary keys.
        """

        subquery = select(self._model_pk_field).select_from(self.__model_cls__)
        subquery = self._apply_filters(subquery, self.__model_cls__, filters)
        return subquery.subquery()

    # ------------------------------------------------------
    # Internal Methods (SQL logic)
    # ------------------------------------------------------

    async def _fetch_by(
            self,
            session: AsyncSession,
            filters: dict[str, Any],
            depth: int = 0,
            limit: int | None = None,
            offset: int | None = None,
            order_by: Sequence[str] | None = None,
    ) -> sqlalchemy.engine.Result[tuple[_modelT]]:
        """
        Internal method to build and execute a SELECT query with filters, ordering, pagination, and relationship loading.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            Filters to apply.

        :param depth: `int`
            Relationship loading depth.

        :param limit: `int | None`
            (Optional) Maximum number of results.

        :param offset: `int | None`
            (Optional) Offset for pagination.

        :param order_by: `Sequence[str] | None`
            (Optional) Ordering criteria.

        :return: `sqlalchemy.engine.Result`
            Query execution result.
        """

        query = select(self.__model_cls__).select_from(self.__model_cls__)
        query = self._apply_filters(query, self.__model_cls__, filters)

        if depth > 0:
            opts = self._build_relationship_load_options(self.__model_cls__, depth)
            query = query.options(*opts)

        if order_by:
            query = self._apply_ordering(query, self.__model_cls__, order_by)

        if offset is not None:
            query = query.offset(offset)

        if limit is not None:
            query = query.limit(limit)

        return await session.execute(query)

    async def _fetch_one_by(
            self,
            session: AsyncSession,
            filters: dict[str, Any],
            depth: int = 0,
            order_by: Sequence[str] | None = None,
    ) -> _modelT | None:
        """
        Fetch a single record matching filters.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            Filters to apply.

        :param depth: `int`
            Relationship loading depth.

        :param order_by: `Sequence[str] | None`
            (Optional) Ordering criteria.

        :return: `_modelT | None`
            The retrieved model instance or None if not found.
        """

        result = await self._fetch_by(session, filters, limit=1, depth=depth, order_by=order_by)
        return result.scalar_one_or_none()

    async def _fetch_many_by(
            self,
            session: AsyncSession,
            filters: dict[str, Any],
            depth: int = 0,
            limit: int | None = None,
            offset: int | None = None,
            order_by: Sequence[str] | None = None,
    ) -> Sequence[_modelT]:
        """
        Fetch multiple records matching filters with optional pagination and ordering.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filtering conditions.

        :param depth: `int`
            The relationship depth to load.

        :param limit: `int | None`
            (Optional) The maximum number of records to return.

        :param offset: `int | None`
            (Optional) The offset for pagination.

        :param order_by: `Sequence[str] | None`
            (Optional) The ordering criteria.

        :return: `Sequence[_modelT]`
            A sequence of fetched records.
        """

        result = await self._fetch_by(session, filters, limit=limit, offset=offset, depth=depth, order_by=order_by)
        return result.scalars().all()

    async def _fetch_by_pk(self, session: AsyncSession, pk: _pkT, depth: int = 0) -> _modelT | None:
        """
        Fetch a record by its primary key with optional relationship loading.

        :param session: `AsyncSession`
            The database session.

        :param pk: `_pkT`
            Primary key of the record.

        :param depth: `int`
            Relationship loading depth.

        :return: `_modelT`
            The retrieved model instance.

        :raises:
            :raise DoesNotExist: If the record is not found.
        """

        query = select(self.__model_cls__).where(self._model_pk_field == pk)

        if depth > 0:
            opts = self._build_relationship_load_options(self.__model_cls__, depth)
            query = query.options(*opts)

        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def _fetch_page(
            self,
            session: AsyncSession,
            filters: dict[str, Any],
            page: int,
            per_page: int,
            depth: int,
            order_by: Sequence[str] | None = None,
    ) -> Sequence[_modelT]:
        """
        Fetch a specific page (offset/limit) of results.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filtering conditions.

        :param order_by: `Sequence[str] | None`
            (Optional) The ordering criteria.

        :param page: `int`
            The page number (1-based index).

        :param per_page: `int`
            The number of records per page.

        :param depth: `int`
            The relationship depth to load.

        :return: `Sequence[_modelT]`
            A sequence of fetched records for the given page.
        """

        offset = (page - 1) * per_page
        return await self._fetch_many_by(session, filters, limit=per_page, offset=offset, depth=depth, order_by=order_by)

    async def _delete_by_pk(self, session: AsyncSession, pk: _pkT) -> _modelT | None:
        """
        Delete a record by its primary key.

        :param session: `AsyncSession`
            The database session.

        :param pk: `_pkT`
            Primary key of the record to delete.

        :return: `_modelT`
            The deleted record.
        """

        result = await session.execute(
            delete(self.__model_cls__)
            .where(self._model_pk_field == pk)
            .returning(self.__model_cls__)
        )

        await session.commit()
        return result.scalar_one_or_none()

    async def _delete_by(self, session: AsyncSession, filters: dict[str, Any]) -> tuple[_modelT, ...]:
        """
        Delete records matching filters.
        Uses a subquery to select primary keys (since DELETE cannot use JOINs directly).

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filtering conditions.

        :return: `tuple[_modelT, ...]`
            A tuple of deleted records.
        """

        subquery = self._build_subquery_for_filters(filters)
        stmt = (
            delete(self.__model_cls__)
            .where(self._model_pk_field.in_(
                select(subquery.c[self._model_pk_field.name])
            ))
            .returning(self.__model_cls__)
        )

        result = await session.execute(stmt)
        return tuple(result.scalars().all())

    async def _update_by_pk(self, session: AsyncSession, pk: _pkT, **fields) -> _modelT | None:
        """
        Update a record by its primary key.

        :param session: `AsyncSession`
            The database session.

        :param pk: `_pkT`
            Primary key of the record.

        :param fields: `dict[str, Any]`
            Fields to update.

        :return: `_modelT`
            The updated record.
        """

        result = await session.execute(
            update(self.__model_cls__)
            .where(self._model_pk_field == pk)
            .values(**fields)
            .returning(self.__model_cls__)
        )

        await session.commit()
        return result.scalar_one_or_none()

    async def _update_by(self, session: AsyncSession, filters: dict[str, Any], update_data: dict[str, Any]) -> _modelT | None:
        """
        Update a record matching filters (which may include nested fields).
        Since UPDATE cannot use JOINs directly, a subquery is used.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filtering conditions to match the record(s) to update.

        :param update_data: `dict[str, Any]`
            The fields to update and their new values.

        :return: `_modelT`
            The updated record.

        :raises:
            :raise DoesNotExist: If no records match the filters.
        """

        subquery = self._build_subquery_for_filters(filters)
        stmt = (
            update(self.__model_cls__)
            .where(self._model_pk_field.in_(
                select(subquery.c[self._model_pk_field.name])
            ))
            .values(**update_data)
            .returning(self.__model_cls__)
        )

        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def _update_model(self, session: AsyncSession, model_obj: _modelT) -> None:
        """
        Merge and commit an updated model instance.

        :param session: `AsyncSession`The retrieved model instance or None if not found.
            The database session.

        :param model_obj: `_modelT`
            The model instance to update and commit.
        """

        await session.merge(model_obj)
        await session.commit()

    async def _create(self, session: AsyncSession, model_obj: _modelT) -> None:
        """
        Insert a new model instance into the database.

        :param session: `AsyncSession`
            The database session.

        :param model_obj: `_modelT`
            The model instance to insert.
        """

        session.add(model_obj)
        await session.commit()

    async def _bulk_create(self, session: AsyncSession, model_objs: Sequence[_modelT]) -> None:
        """
        Bulk insert multiple model instances within a provided session.

        :param session: `AsyncSession`
            The database session to use for the transaction.

        :param model_objs: `Sequence[_modelT]`
            A sequence of model instances to be inserted into the database.
        """

        session.add_all(model_objs)
        await session.commit()

    async def _bulk_update(self, session: AsyncSession, filters: dict[str, Any], update_data: dict[str, Any]) -> int:
        """
        Perform a bulk update of record matching filters.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filters used to identify the records to update.

        :param update_data: `dict[str, Any]`
            The data to update in the selected records.

        :return: `int`
            The number of rows updated.
        """

        subquery = self._build_subquery_for_filters(filters)
        stmt = (
            update(self.__model_cls__)
            .where(self._model_pk_field.in_(
                select(subquery.c[self._model_pk_field.name])
            ))
            .values(**update_data)
        )
        result = await session.execute(stmt)
        await session.commit()
        return result.rowcount  # type: ignore

    async def _count(self, session: AsyncSession, filters: dict[str, Any]) -> int:
        """
        Count the number of record matching filters.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filters used to match the records to count.

        :return: `int`
            The count of records matching the filters.
        """

        query = select(func.count()).select_from(self.__model_cls__)
        query = self._apply_filters(query, self.__model_cls__, filters)
        result = await session.execute(query)
        return result.scalar_one()

    async def _exists(self, session: AsyncSession, filters: dict[str, Any]) -> bool:
        """
        Check if record matching filters exist.

        :param session: `AsyncSession`
            The database session.

        :param filters: `dict[str, Any]`
            The filters used to match the record to check for existence.

        :return: `bool`
            `True` if a matching record exists, otherwise `False`.
        """

        query = select(self._model_pk_field).select_from(self.__model_cls__)
        query = self._apply_filters(query, self.__model_cls__, filters)
        result = await session.execute(query.limit(1))
        return result.scalar_one_or_none() is not None

    # ------------------------------------------------------
    # Public Methods
    # ------------------------------------------------------

    async def create(self, model_obj: _modelT) -> None:
        """
        Save a model instance to the database.

        :param model_obj: `_modelT`
            The model instance to save.
        """

        async with self.__db_manager__.transaction() as session:
            await self._create(session, model_obj)

    async def bulk_create(self, model_objs: Sequence[_modelT]) -> None:
        """
        Bulk insert multiple model instances in a single transaction.

        :param model_objs: `Sequence[_modelT]`
            A sequence of model instances to insert into the database.
        """

        async with self.__db_manager__.transaction() as session:
            await self._bulk_create(session, model_objs)

    def paginate(self, per_page: int = 10, depth: int = 0, order_by: Sequence[str] | None = None, **filters) -> LazyPaginator[_modelT]:
        """
        Return a lazy paginator that loads pages on demand.

        :param per_page: int
            The number of records per page

        :param depth: int
            The depth of related data to fetch

        :param order_by: Sequence[str] | None
            (Optional) list of fields to order the results by.

        :param filters: dict[str, Any]
            (Optional) Key-value pairs used to filter the records.

        :return: LazyPaginator[_modelT]
            A lazy paginator that can be used to load paginated records.
        """

        return LazyPaginator(
            paginateable=self,
            filters=filters,
            order_by=order_by,
            per_page=per_page,
            depth=depth,
        )

    async def get_page(
            self,
            filters: dict[str, Any],
            page: int,
            per_page: int,
            depth: int,
            order_by: Sequence[str] | None = None
    ) -> Sequence[_modelT]:
        """
        Fetch a specific page (offset/limit) of results.

        :param filters: `dict[str, Any]`
            The filtering conditions.

        :param page: `int`
            The page number (1-based index).

        :param per_page: `int`
            The number of records per page.

        :param depth: `int`
            The relationship depth to load.

        :param order_by: `Sequence[str] | None`
            (Optional) The ordering criteria.

        :return: `Sequence[_modelT]`
            A sequence of fetched records for the given page.
        """

        async with self.__db_manager__.session() as session:
            return await self._fetch_page(session, filters, page, per_page, depth, order_by)

    async def get_by_pk(self, pk: _pkT, depth: int = 0) -> _modelT | None:
        """
        Retrieve a record by its primary key.

        :param pk: `_pkT`
            Primary key of the record.

        :param depth: `int`
            Relationship loading depth.

        :return: `_modelT | None`
            The retrieved model instance or None if not found.
        """

        async with self.__db_manager__.session() as session:
            return await self._fetch_by_pk(session, pk, depth=depth)

    async def get_by_pk_strict(self, pk: _pkT, depth: int = 0) -> _modelT:
        """
        Fetch a record by primary key.
        Raises an exception if not found.

        :param pk: `_pkT`
            The primary key of the record to fetch.

        :param depth: `int`
            The depth of related data to fetch, defaults to 0.

        :raises:
            :raise DoesNotExist: If no record is found.

        :return:
            The fetched model instance.
        """

        if (fetched := await self.get_by_pk(pk, depth=depth)) is not None:
            return fetched

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with pk={pk}")

    async def get_one_by(self, depth: int = 0, order_by: Sequence[str] | None = None, **filters) -> _modelT | None:
        """
        Fetch a single record matching filters.

        :param filters: `dict[str, Any]`
            Filters to apply.

        :param depth: `int`
            Relationship loading depth.

        :param order_by: `Sequence[str] | None`
            (Optional) Ordering criteria.

        :return: `_modelT | None`
            The retrieved model instance or None if not found.
        """

        async with self.__db_manager__.session() as session:
            return await self._fetch_one_by(session, filters, depth=depth, order_by=order_by)

    async def get_one_by_strict(self, depth: int = 0, order_by: Sequence[str] | None = None, **filters) -> _modelT:
        """
        Fetch a single record matching filters.
        Raises an exception if no record is found.

        :param depth: `int`
            The depth of related data to fetch.

        :param order_by: `Sequence[str] | None`
            (Optional) list of fields to order the results by.

        :param filters: `dict[str, Any]`
            Key-value pairs used to filter the records.

        :return: `_modelT`
            The fetched record if found.

        :raises:
            :raise DoesNotExist: If no record matches the filters.
        """

        if (fetched := await self.get_one_by(depth=depth, order_by=order_by, **filters)) is not None:
            return fetched

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} by filters={filters}")

    async def get_many_by(
            self,
            *,
            depth: int = 0,
            __limit__: int | None = None,
            __offset__: int | None = None,
            order_by: Sequence[str] | None = None,
            **filters,
    ) -> Sequence[_modelT]:
        """
        Fetch multiple records based on filters, with optional pagination and ordering.

        :param depth: int
            The depth of related data to fetch.

        :param __limit__: `int | None`
            (Optional) limit for the number of records to fetch.

        :param __offset__: `int | None`
            (Optional) offset for pagination.

        :param order_by: `Sequence[str] | None`
            (Optional) list of fields to order the results by.

        :param filters: `dict[str, Any]`
            Key-value pairs used to filter the records.

        :return: `Sequence[_modelT]`
            A list of fetched records matching the filters.
        """

        async with self.__db_manager__.session() as session:
            return await self._fetch_many_by(session, filters, limit=__limit__, offset=__offset__, depth=depth, order_by=order_by)

    async def get_many_by_strict(
            self,
            *,
            depth: int = 0,
            __limit__: int | None = None,
            __offset__: int | None = None,
            order_by: Sequence[str] | None = None,
            **filters,
    ) -> Sequence[_modelT]:
        """
        Fetch multiple records based on filters, with optional pagination and ordering.
        Raise an exception if no records are found.

        :param depth: `int`
            The depth level for related object fetching.

        :param __limit__: `int | None`
            The maximum number of records to fetch. Defaults to None.

        :param __offset__: `int | None`
            The offset for pagination. Defaults to None.

        :param order_by: `Sequence[str] | None`
            (Optional) A list of fields to order the results by. Defaults to None.

        :param filters: `dict[str, Any]`
            The filter conditions for fetching records.

        :return: `Sequence[_modelT]`
            The fetched records.

        :raises:
            :raise DoesNotExist: If no records are found matching the filters.
        """

        if fetched := await self.get_many_by(depth=depth, limit=__limit__, offset=__offset__, order_by=order_by, **filters):
            return fetched

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} by filters={filters}")

    async def update(self, model_obj: _modelT, **fields) -> None:
        """
        Update a model instance by setting attributes.

        :param model_obj: `_modelT`
            The model instance to update.

        :param fields: `dict[str, Any]`
            Key-value pairs representing the fields and their new values to update.
        """

        for key, value in fields.items():
            setattr(model_obj, key, value)

        async with self.__db_manager__.transaction() as session:
            await self._update_model(session, model_obj)

    async def update_by_pk(self, pk: _pkT, **fields) -> _modelT | None:
        """
        Update a record by its primary key.

        :param pk: `_pkT`
            The primary key of the record to update.

        :param fields: `dict[str, Any]`
            Key-value pairs representing the fields and their new values to update.

        :return: `_modelT | None`
            The updated model instance or None if not found.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._update_by_pk(session, pk, **fields)

    async def update_by_pk_strict(self, pk: _pkT, **fields) -> _modelT:
        """
        Update a record by its primary key.
        Raise an exception if no records are found.

        :param pk: `_pkT`
            The primary key of the record to update.

        :param fields: `dict[str, Any]`
            Key-value pairs representing the fields and their new values to update.

        :return: `_modelT`
            The updated model instance.

        :raises:
            :raise DoesNotExist: If no record is found.
        """

        if (updated := await self.update_by_pk(pk, **fields)) is not None:
            return updated

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with pk={pk}")

    async def update_by(self, update_data: dict[str, Any], **filters) -> _modelT | None:
        """
        Update a record matching filters.

        :param update_data: `dict[str, Any]`
            A dictionary of fields and their new values to update in the record.

        :param filters: `dict[str, Any]`
            Key-value pairs representing the filters used to find the record to update.

        :return: `_modelT | None`
            The updated model instance.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._update_by(session, filters, update_data)

    async def update_by_strict(self, update_data: dict[str, Any], **filters) -> _modelT:
        """
        Update a record matching filters.
        Raise an exception if no records are found.

        :param update_data: `dict[str, Any]`
            A dictionary of fields and their new values to update in the record.

        :param filters: `dict[str, Any]`
            Key-value pairs representing the filters used to find the record to update.

        :return: `_modelT`
            The updated model instance.

        :raises:
            :raise DoesNotExist: If no record is found.
        """

        if updated := await self.update_by(update_data, **filters):
            return updated

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with filters={filters}")

    async def bulk_update(self, update_data: dict[str, Any], **filters) -> int:
        """
        Bulk update records matching filters.
        Returns the number of rows updated.

        :param update_data: `dict[str, Any]`
            A dictionary of fields and their new values to update in the records.

        :param filters: `dict[str, Any]`
            Key-value pairs representing the filters used to select the records to update.

        :return: `int`
            The number of rows updated.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._bulk_update(session, filters, update_data)

    async def delete(self, model_obj: _modelT) -> None:
        """
        Delete a model instance.

        :param model_obj: `_modelT`
            The model instance to delete from the database.
        """

        async with self.__db_manager__.transaction() as session:
            await session.delete(model_obj)

    async def delete_by_pk(self, pk: _pkT) -> _modelT | None:
        """
        Delete a record by its primary key.

        :param pk: `_pkT`
            The primary key of the record to delete.

        :return: `_modelT | None`
            The deleted model instance or None if not found.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._delete_by_pk(session, pk)

    async def delete_by_pk_strict(self, pk: _pkT) -> _modelT:
        """
        Delete a record by its primary key.
        Raise an exception if no records are found.

        :param pk: `_pkT`
            The primary key of the record to delete.

        :return: `_modelT`
            The deleted model instance or None if not found.

        :raises:
            :raise DoesNotExist: If no record is found.
        """

        if (deleted := await self.delete_by_pk(pk)) is not None:
            return deleted

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with pk={pk}")

    async def delete_by(self, **filters) -> tuple[_modelT, ...]:
        """
        Delete records matching filters.

        :param filters: `dict[str, Any]`
            The filter conditions for selecting records to delete.

        :return: `tuple[_modelT, ...]`
            The deleted records.
        """

        async with self.__db_manager__.transaction() as session:
            return await self._delete_by(session, filters)

    async def delete_by_strict(self, **filters) -> tuple[_modelT, ...]:
        """
        Delete records matching filters.

        :param filters: `dict[str, Any]`
            The filter conditions for selecting records to delete.

        :return: `tuple[_modelT, ...]`
            The deleted records.

        :raises:
            :raise DoesNotExist: If no record is found.
        """

        if deleted := await self.delete_by(**filters):
            return deleted

        raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with filters={filters}")

    async def count(self, **filters) -> int:
        """
        Count the number of record matching filters.

        :param filters: `dict[str, Any]`
            The filter conditions for counting the records.

        :return: `int`
            The number of records matching the filters.
        """

        async with self.__db_manager__.session() as session:
            return await self._count(session, filters)

    async def exists(self, **filters) -> bool:
        """
        Check if at least one record exists matching filters.

        :param filters: `dict[str, Any]`
            The filter conditions to check the existence of records.

        :return: `bool`
            Returns True if at least one record matches the filters, False otherwise.
        """

        async with self.__db_manager__.session() as session:
            return await self._exists(session, filters)

    async def must_exist(self, **filters) -> None:
        """
        Check if at least one record exists matching filters.
        If no record exists, raise an exception.

        :param filters: `dict[str, Any]`
            The filter conditions to check the existence of records.

        :raises:
            :raise DoesNotExist: If no record matches the provided filters.
        """

        if not self.exists(**filters):
            raise self.__model_cls__.DoesNotExist(f"Not found {self.__model_cls__.__name__} with filters={filters}")
