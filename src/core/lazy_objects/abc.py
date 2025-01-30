from abc import ABC, abstractmethod
from typing import Any


class AbstractLazyObject[_T](ABC):
    """
    An abstract base class for lazy evaluation of objects.

    Subclasses must implement the abstract methods:
    - `object_name(self) -> str`: Returns the name of the lazy object.
    - `get(self) -> _T`: Retrieves and returns the actual value of the lazy object.
    - `get_safe(self) -> _T | None`: Retrieves and returns the actual value of the lazy object, or None if not available.
    """

    @property
    @abstractmethod
    def object_name(self) -> str:
        """
        Returns the name of the lazy object.

        :return: `str`
            The name of the lazy object.
        """

    @abstractmethod
    def get(self) -> _T:
        """
        Retrieves and returns the actual value of the lazy object.

        :return: `_T`
            The actual value of the lazy object.
        """

    @abstractmethod
    def get_safe(self) -> _T | None:
        """
        Retrieves and returns the actual value of the lazy object safely.

        :return: `_T | None`
            The actual value of the lazy object if available, otherwise None.
        """

    def __get__(self, instance: Any | None, owner: type[Any]) -> _T:
        """
        Default implementation for the descriptor protocol.

        :return: `_T`
            The actual value of the lazy object.
        """

        return self.get()
