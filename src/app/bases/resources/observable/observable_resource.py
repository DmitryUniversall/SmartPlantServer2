from abc import ABC
from collections import defaultdict
from typing import Any, Callable
from typing import override

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.bases.db import BaseModel
from src.app.bases.resources.base import BaseResource
from .event_type import ResourceEventType
from .observer import ResourceEventObserver


class ObservableResource[_modelT: BaseModel, _pkT: Any](BaseResource[_modelT, _pkT], ABC):
    def __init__(self):
        """
        Initializes ObservableResource
        """

        self._event_listeners: defaultdict[ResourceEventType, list[ResourceEventObserver]] = defaultdict(list)

    @override
    async def _delete_by_pk(self, session: AsyncSession, pk: _pkT) -> _modelT:
        """
        Deletes a model object by primary key and trigger pre/post-delete events.

        :param session: `AsyncSession`
            Database session used for deletion.

        :param pk: `_pkT`
            The primary key of the record to delete.

        :return: `_modelT`
            The deleted record.
        """

        await self._call_event(event_type=ResourceEventType.PRE_DELETE, pk=pk, session=session)
        deleted = await super()._delete_by_pk(session, pk)
        await self._call_event(event_type=ResourceEventType.POST_DELETE, deleted=deleted, session=session)

        return deleted

    @override
    async def _update_by_pk(self, session: AsyncSession, pk: _pkT, **fields) -> _modelT:
        """
        Updates a model object by primary key and trigger pre/post-update events.

        :param session: `AsyncSession`
            Database session used for updating.

        :param pk: `_pkT`
            The primary key of the record to update.

        :param fields: `dict`
            The fields to update with their new values.

        :return: `_modelT`
            The updated record.
        """

        await self._call_event(event_type=ResourceEventType.PRE_UPDATE, updating=pk, session=session)
        updated = await super()._update_by_pk(session, pk, **fields)
        await self._call_event(event_type=ResourceEventType.POST_UPDATE, updated=updated, session=session)

        return updated

    @override
    async def _update_model(self, session: AsyncSession, model_obj: _modelT) -> None:
        """
        Updates an existing model and trigger pre/post-update events.

        :param session: `AsyncSession`
            Database session used for updating.

        :param model_obj: `_modelT`
            The model instance to update.
        """

        await self._call_event(event_type=ResourceEventType.PRE_UPDATE, updating=model_obj, session=session)
        await super()._update_model(session, model_obj)
        await self._call_event(event_type=ResourceEventType.POST_UPDATE, updated=model_obj, session=session)

    @override
    async def _create(self, session: AsyncSession, model_obj: _modelT) -> None:
        """
        Inserts a new model instance into the database and trigger pre/post-create events.

        :param session: `AsyncSession`
            Database session used for insertion.

        :param model_obj: `_modelT`
            The model instance to insert.
        """

        await self._call_event(event_type=ResourceEventType.PRE_CREATE, creating=model_obj, session=session)
        await super()._create(session, model_obj)
        await self._call_event(event_type=ResourceEventType.POST_CREATE, created=model_obj, session=session)

    async def _call_event(self, event_type: ResourceEventType, *args, **kwargs) -> None:
        """
        Calls all observers associated with a given event type.

        :param event_type: `ResourceEventType`
            The type of event to trigger.

        :param args: `tuple`
            Positional arguments to pass to event observers.

        :param kwargs: `dict`
            Keyword arguments to pass to event observers.
        """

        observers = self._event_listeners[event_type]

        for observer in observers:
            await observer(*args, **kwargs)

    def listen(self, event_type: ResourceEventType) -> Callable[[ResourceEventObserver], ResourceEventObserver]:
        """
        Decorator to register an event listener for a specific event type.

        :param event_type: `ResourceEventType`
            The event type to listen for.

        :return: `Callable[[ResourceEventObserver], ResourceEventObserver]`
            A decorator that registers an event observers for the given event type.
        """

        def decorator(coro):
            self._event_listeners[event_type].append(coro)
            return coro

        return decorator
