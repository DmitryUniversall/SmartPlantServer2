import functools
import inspect
import logging
import warnings
from typing import Callable

from src.core.exceptions.generics import NoneObjectError

_logger = logging.getLogger(__name__)


def default_any[_T](
        value: _T | None,
        *defaults: *tuple[_T, ...]
) -> _T:
    """
    Returns value if value is not None, in other case returns first not-None default

    :param value: `_T | None`
        Initial value

    :param defaults: `*tuple[_T, ...]`
        Default values

    :return: `_T`
        Returns value if value is not None, in other case returns first not-None default

    :raises:
        :raise NoneObjectError: If all default values are None
    """

    if value is not None:
        return value

    for default_value in defaults:
        if default_value is not None:
            return default_value

    raise NoneObjectError("All default values are None")


def deprecated(
        reason: str | type | Callable,
        warning_format: str = "Called deprecated {kind} {name}: {reason}"
):
    """
    Decorator function to mark a function or class as deprecated and issue a warning when it is called.

    :param reason: `str | type | Callable`
        The reason for deprecation, or a class/function to deprecate.

    :param warning_format: `str`
        The format string for the deprecation warning message.

    :return: `Callable`
        A decorated function or class.

    :raises:
        :raise TypeError: If the provided 'reason' argument is of an unsupported type.
    """

    def decorator(func):
        @functools.wraps(func)
        def new_func(*args, **kwargs):
            name = func.__name__
            kind = 'class' if inspect.isclass(func) else 'function'
            msg = reason if isinstance(reason, str) else f"{kind} is deprecated"

            warnings.simplefilter('always', DeprecationWarning)
            warnings.warn(
                message=warning_format.format(kind=kind, name=name, reason=msg),
                category=DeprecationWarning,
                stacklevel=2
            )
            warnings.simplefilter('default', DeprecationWarning)

            return func(*args, **kwargs)

        return new_func

    if isinstance(reason, str):
        return decorator
    elif isinstance(reason, type) or callable(reason):
        return decorator(reason)
    else:
        raise TypeError(repr(type(reason)))
