from abc import ABC, abstractmethod
from typing import Any, Sequence

from src.app.bases.db import BaseModel


class DBPaginateable[_modelT: BaseModel](ABC):
    @abstractmethod
    async def get_page(
            self,
            filters: dict[str, Any],
            page: int,
            per_page: int,
            depth: int,
            order_by: Sequence[str] | None = None
    ) -> Sequence[_modelT]:
        ...

    @abstractmethod
    async def count(self, **filters) -> int:
        ...
