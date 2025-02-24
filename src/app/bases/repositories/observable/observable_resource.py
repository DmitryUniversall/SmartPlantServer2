import inspect
from abc import ABC
from typing import Any, Callable, Sequence
from typing import override

from src.app.bases.db import BaseModel
from .event_type import RepositoryEventType
from .. import BaseRepository


class ObservableRepository[_modelT: BaseModel, _pkT: Any](BaseRepository[_modelT, _pkT], ABC):
    """
    An observable resource extends BaseRepository to provide event notifications.
    You can register listeners for events (using the `listen` decorator)
    that will be called before/after create, update, or delete operations.
    """

    def __init__(self) -> None:
        super().__init__()

        self._listeners: dict[RepositoryEventType, list[Callable[..., Any]]] = {}

    def listen(self, event_type: RepositoryEventType) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """
        Decorator to register a listener for a specific resource event.

        Example:

            @resource.listen(ResourceEventType.PRE_CREATE)
            async def on_pre_create(*, model_obj):
                ...
        """

        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self._listeners.setdefault(event_type, []).append(func)
            return func

        return decorator

    async def _notify_listeners(self, event_type: RepositoryEventType, **kwargs: Any) -> None:
        """
        Call all registered listeners for the given event type.
        If a listener returns an awaitable, it is awaited.
        """

        for listener in self._listeners.get(event_type, []):
            result = listener(**kwargs)
            if inspect.isawaitable(result):
                await result

    @override
    async def create(self, model_obj: _modelT) -> None:
        await self._notify_listeners(RepositoryEventType.PRE_CREATE, model_obj=model_obj)
        await super().create(model_obj)
        await self._notify_listeners(RepositoryEventType.POST_CREATE, model_obj=model_obj)

    @override
    async def bulk_create(self, model_objs: Sequence[_modelT]) -> None:
        await self._notify_listeners(RepositoryEventType.PRE_BULK_CREATE, model_objs=model_objs)
        await super().bulk_create(model_objs)
        await self._notify_listeners(RepositoryEventType.POST_BULK_CREATE, model_objs=model_objs)

    @override
    async def update(self, model_obj: _modelT, **fields) -> None:
        await self._notify_listeners(RepositoryEventType.PRE_UPDATE, model_obj=model_obj, fields=fields)
        await super().update(model_obj, **fields)
        await self._notify_listeners(RepositoryEventType.POST_UPDATE, model_obj=model_obj, fields=fields)

    @override
    async def update_by_pk(self, pk: _pkT, **fields) -> _modelT | None:
        await self._notify_listeners(RepositoryEventType.PRE_UPDATE, pk=pk, fields=fields)
        result = await super().update_by_pk(pk, **fields)
        await self._notify_listeners(RepositoryEventType.POST_UPDATE, pk=pk, fields=fields, result=result)
        return result

    @override
    async def update_by(self, update_data: dict[str, Any], **filters) -> _modelT | None:
        await self._notify_listeners(RepositoryEventType.PRE_UPDATE, update_data=update_data, filters=filters)
        result = await super().update_by(update_data, **filters)
        await self._notify_listeners(RepositoryEventType.POST_UPDATE, update_data=update_data, filters=filters, result=result)
        return result

    @override
    async def update_by_strict(self, update_data: dict[str, Any], **filters) -> _modelT:
        await self._notify_listeners(RepositoryEventType.PRE_UPDATE, update_data=update_data, filters=filters)
        result = await super().update_by_strict(update_data, **filters)
        await self._notify_listeners(RepositoryEventType.POST_UPDATE, update_data=update_data, filters=filters, result=result)
        return result

    @override
    async def bulk_update(self, update_data: dict[str, Any], **filters) -> int:
        await self._notify_listeners(RepositoryEventType.PRE_BULK_UPDATE, update_data=update_data, filters=filters)
        result = await super().bulk_update(update_data, **filters)
        await self._notify_listeners(RepositoryEventType.POST_BULK_UPDATE, update_data=update_data, filters=filters, result=result)
        return result

    @override
    async def delete(self, model_obj: _modelT) -> None:
        await self._notify_listeners(RepositoryEventType.PRE_DELETE, model_obj=model_obj)
        await super().delete(model_obj)
        await self._notify_listeners(RepositoryEventType.POST_DELETE, model_obj=model_obj)

    @override
    async def delete_by_pk(self, pk: _pkT) -> _modelT | None:
        await self._notify_listeners(RepositoryEventType.PRE_DELETE, pk=pk)
        result = await super().delete_by_pk(pk)
        await self._notify_listeners(RepositoryEventType.POST_DELETE, pk=pk, result=result)
        return result

    @override
    async def delete_by(self, **filters) -> tuple[_modelT, ...]:
        await self._notify_listeners(RepositoryEventType.PRE_DELETE, filters=filters)
        result = await super().delete_by(**filters)
        await self._notify_listeners(RepositoryEventType.POST_DELETE, filters=filters, result=result)
        return result
