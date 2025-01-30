from abc import ABC, abstractmethod
from functools import wraps
from typing import Callable, Self

from fastapi.responses import Response


class AbstractErrorHandler[_errorT: Exception](ABC):
    """
    An abstract base class for handling errors asynchronously, defining a structure for custom error handlers.
    """

    # FIXME: Add valid return type (like 'Callable[..., AbstractErrorHandler[_T]]')
    @classmethod
    def as_error_handler[_T: Exception](cls, exception_cls: type[_T], **init_kwargs) -> Callable:
        """
        Decorator that creates a custom error handler based on the given exception class.

        :param exception_cls: `type[_T]`
            The class of the exception this handler will manage.

        :param init_kwargs: `dict`
            Additional initialization arguments for the handler class.

        :return: `Callable[..., AbstractErrorHandler[_T]]`
            A decorator function that can be applied to a coroutine handler function.
        """

        def decorator(coro) -> type[Self]:
            @wraps(coro)
            async def wrapper(handler_self: 'AbstractErrorHandler', *args, **kwargs) -> Response:
                return await coro(*args, **kwargs, handler=handler_self)

            handler = type(coro.__name__, (cls,), {
                '__exception_cls__': exception_cls,
                'handle': wrapper
            })

            return handler(**init_kwargs)

        return decorator

    @property
    @abstractmethod
    def __exception_cls__(self) -> type[_errorT]:
        """
        Abstract property that must return the exception class this handler is responsible for.

        :return: `type[_errorT]`
            The class of the exception this handler will manage.
        """

    @abstractmethod
    async def handle(self, error: _errorT) -> Response:
        """
        Abstract method to handle an exception.

        :param error: `_errorT`
            The exception to handle.

        :return: `Response`
            The http response resulting from handling the exception.
        """

    async def __call__(self, *args, **kwargs) -> Response:
        """
        Allows the instance to be called directly, invoking the `handle` method.

        :param args: `tuple`
            Positional arguments passed to the `handle` method.

        :param kwargs: `dict`
            Keyword arguments passed to the `handle` method.

        :return: `Response`
            The response resulting from handling the exception.
        """

        return await self.handle(*args, **kwargs)
