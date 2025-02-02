from abc import abstractmethod
from typing import Any, Protocol, TypeVar, TypeAlias

_sizedIndexableReturnT = TypeVar("_sizedIndexableReturnT", covariant=True)


class SizedIndexable(Protocol[_sizedIndexableReturnT]):
    """
    A protocol for objects that are sized and indexable.
    """

    @abstractmethod
    def __len__(self) -> int:
        ...

    @abstractmethod
    def __getitem__(self, index: int) -> _sizedIndexableReturnT:
        ...


class _MissingSentinel:
    """
    A special sentinel class representing a missing value.

    This class is used as a placeholder to indicate the absence of a value,
    particularly useful when `None` is a valid input or default value.
    """

    __slots__ = ()

    def __bool__(self) -> bool:
        return False

    def __hash__(self) -> int:
        return 0

    def __repr__(self) -> str:
        return "..."

    def __str__(self) -> str:
        return "..."


MISSING: Any = _MissingSentinel()
JsonDict: TypeAlias = dict[str, Any]
UUIDString: TypeAlias = str
