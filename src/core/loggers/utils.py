import inspect
import logging
from functools import wraps
from typing import Any


def log_async_methods(
        logger_name: str | None = None,
        log_result: bool = False,
        log_level: int = logging.DEBUG
):
    """
    A decorator function for logging all async methods of class.

    :param logger_name: `str | None`
        The custom name of the logger, where the logs will be pushed. If not given,
        a logger taking the name of the class and the module will be created.

    :param log_result: `bool`
        A flag to determine whether the results of the async operations should be logged or not.
        By default, False.

    :param log_level: `int`
        The logging level.
        By default, logging.DEBUG.

    :return: `cls`
        The original class with wrapped coroutine functions that logs when called and possibly their results.
    """

    def decorator(cls):
        def get_wrapper(func):
            logger = logging.getLogger(
                logger_name if logger_name is not None else f"async_calls.{cls.__module__}.{cls.__name__}")

            @wraps(func)
            async def wrapper(*args, **kwargs) -> Any:
                logger.log(log_level, f"Called method {func.__name__} of class {cls.__name__}")

                result = await func(*args, **kwargs)

                if log_result:
                    logger.log(log_level, f"Got result form method {func.__name__} of class {cls.__name__}: {result}")

                return result

            return wrapper

        for attr in dir(cls):
            if attr.startswith("__"):
                continue

            value = getattr(cls, attr)

            if inspect.iscoroutinefunction(value):
                setattr(cls, attr, get_wrapper(value))

        return cls

    return decorator
