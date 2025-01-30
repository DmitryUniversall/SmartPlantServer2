import logging
from contextlib import contextmanager
from traceback import format_exception
from typing import Generator


def get_traceback_text(error: BaseException) -> str:
    """
    Returns the traceback text of an exception.

    :param error: `BaseException`
        The exception from which to get the traceback text.

    :return: `str`
        The formatted traceback text.
    """

    return "".join(format_exception(type(error), error, error.__traceback__))


@contextmanager
def supress_exception(
        exception: type[BaseException] | tuple[type[BaseException], ...],
        logger: logging.Logger | None = None
) -> Generator[None, None, None]:
    """
    A context manager to suppress specified exceptions.

    :param exception: `type[BaseException] | tuple[type[BaseException], ...]`
        The exception type(s) to suppress.

    :param logger: `logging.Logger | None`
        (Optional) A logger instance to log the suppressed exception.
        By default, `None` (no logging).

    :yield: `None`
        Allows the execution of code within the context.
    """

    try:
        yield
    except exception as error:
        if logger:
            logger.debug(f"Suppressing exception {error.__class__.__name__}: {error}")
