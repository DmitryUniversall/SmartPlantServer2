from contextlib import asynccontextmanager
from logging import getLogger
from typing import AsyncGenerator, AsyncContextManager

from sqlalchemy.exc import IntegrityError, StatementError
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.utils.errors import get_traceback_text

_logger = getLogger(__name__)


@asynccontextmanager
async def transaction_session(
        context_manager: AsyncContextManager[AsyncSession]
) -> AsyncGenerator[AsyncSession, None]:
    """
    A context manager that ensures automatic rollback and closure of an async database session.

    :param context_manager: `AsyncContextManager[AsyncSession]`
        The asynchronous context manager that provides a database session.

    :yield: `AsyncSession`
        The database session to be used within the context.
    """

    async with context_manager as session:
        async with session.begin():
            yield session


@asynccontextmanager
async def async_session_error_convert_wrapper(
        context_manager: AsyncContextManager[AsyncSession],
        error_mapping: dict[str, type[StatementError]]
) -> AsyncGenerator[AsyncSession, None]:
    """
    A context manager that converts specific database integrity errors into custom exceptions
    and ensures the session is closed after usage.

    :param context_manager: `AsyncContextManager[AsyncSession]`
        The asynchronous context manager that provides a database session.

    :param error_mapping: `dict[str, type[StatementError]]`
        Dictionary mapping database integrity errors to custom exception classes.

    :yield: `AsyncSession`
        The database session to be used within the context.

    :raises Exception:
        - Custom exceptions mapped from `IntegrityError` based on `error_mapping`.
        - The original exception if no mapping is found.
    """

    async with context_manager as session:
        try:
            yield session
        except IntegrityError as error:
            for key, value in error_mapping.items():
                if key not in str(error.orig).lower():
                    continue

                _logger.debug(f"Converting db error {error.orig.__class__.__name__} to {value.__name__} ({error.orig})")
                raise value(
                    message=str(error),
                    statement=error.statement,
                    params=error.params,
                    orig=error.orig,
                    hide_parameters=error.hide_parameters,
                    code=error.code,
                    ismulti=error.ismulti,
                )

            _logger.debug(f"Unknown error during db session:\n{get_traceback_text(error)}")
            raise error
        finally:
            await session.close()
