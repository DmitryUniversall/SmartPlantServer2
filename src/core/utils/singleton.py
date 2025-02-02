from abc import ABCMeta
from typing import Any


class SingletonMeta(type):
    """
    A metaclass for creating Singleton classes. Ensures that only one instance of a class is created.
    """

    _instances: dict[type[Any], Any] = {}

    def __call__(cls, *args, **kwargs) -> Any:
        """
        Controls the instantiation of the class, ensuring only one instance exists.

        :param args: `tuple`
            Positional arguments for the class constructor.

        :param kwargs: `dict`
            Keyword arguments for the class constructor.
        """

        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class ABCSingletonMeta(ABCMeta, SingletonMeta):
    """
    A metaclass that combines Singleton behavior with Abstract Base Class behavior.

    Inheriting from both SingletonMeta and ABCMeta allows Singleton to be used as a base class for abstract subclasses.
    """
