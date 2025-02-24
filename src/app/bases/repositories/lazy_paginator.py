from typing import Any, TYPE_CHECKING, Sequence

from src.app.bases.db import BaseModel

if TYPE_CHECKING:
    from .base import BaseRepository


class LazyPaginator[_modelT: BaseModel]:
    """
    A lazy paginator that loads pages on demand.
    Each page is fetched when iterated over.
    """

    def __init__(
            self,
            repository: 'BaseRepository[_modelT, Any]',
            filters: dict[str, Any],
            per_page: int,
            depth: int,
            order_by: Sequence[str] | None = None,
    ) -> None:
        """
        Initialize the paginator with resource and pagination settings.

        :param repository: `BaseRepository[_modelT, Any]`
            The resource to paginate, typically a class that provides methods like `get_page` and `count`.

        :param filters: `dict[str, Any]`
            The filter conditions to apply when fetching records.

        :param per_page: `int`
            The number of records to fetch per page.

        :param depth: `int`
            The depth of related records to fetch.

        :param order_by: `Sequence[str] | None`
            The optional ordering criteria for the results.
        """

        self._resource: 'BaseRepository[_modelT, Any]' = repository
        self._filters: dict[str, Any] = filters
        self._per_page: int = per_page
        self._depth: int = depth
        self._page: int = 1
        self._total: int | None = None
        self._order_by: Sequence[str] | None = order_by

    async def total(self) -> int:
        """
        Get the total number of records matching the filters.

        :return: int
            The total number of records matching the filters.
        """

        if self._total is None:
            self._total = await self._resource.count(**self._filters)

        return self._total

    async def get_page(self, page: int) -> Sequence[_modelT]:
        """
        Fetch a specific page of results based on the paginator settings.

        :param page: `int`
            The page number to fetch (1-based index).

        :return: `Sequence[_modelT]`
            The fetched records corresponding to the page.
        """

        return await self._resource.get_page(self._filters, page, self._per_page, self._depth, self._order_by)

    async def __aiter__(self):
        """
        Initialize the paginator for iteration. Starts at page 1.

        :return: LazyPaginator[_modelT]
            The paginator instance.
        """

        self._page = 1
        return self

    async def __anext__(self) -> Sequence[_modelT]:
        """
        Get the next page of results.

        :return: Sequence[_modelT]
            The records for the current page.
        """

        page_data = await self.get_page(self._page)

        if not page_data:
            raise StopAsyncIteration

        self._page += 1
        return page_data
