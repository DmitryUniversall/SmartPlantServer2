from typing import Any
from abc import ABC, abstractmethod


class AbstractConfig(ABC):
    """
    Abstract base class for configuration classes.
    """

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """
        Abstract method to be implemented by subclasses.
        Loads and returns configuration data.

        :return: `dict[str, Any]`
            A dictionary containing configuration data.
        """
