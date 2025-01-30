from abc import ABCMeta
from logging import getLogger
from typing import Callable, AsyncContextManager, Generator, Any, Self

from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.app.bases.db import AbstractAsyncDatabaseManager
from src.app.bases.db import async_session_error_convert_wrapper
from src.app.main.db.exceptions import error_mapping
from src.core.exceptions import InitializationError
from src.core.state import project_settings
from src.core.utils.singleton import SingletonMeta

_logger = getLogger(__name__)


class _AsyncDatabaseManagerSTMeta(ABCMeta, SingletonMeta):
    """
    Metaclass combining `ABCMeta` and `SingletonMeta` for managing the singleton
    and abstract base class behavior for `AsyncDatabaseManagerST`.
    """


class AsyncDatabaseManagerST(AbstractAsyncDatabaseManager, metaclass=_AsyncDatabaseManagerSTMeta):
    """
    A singleton database manager for managing asynchronous database connections and sessions.

    Note: ASYNC INITIALISATION REQUIRED
    """

    def __init__(self) -> None:
        """
        Initializes the `AsyncDatabaseManagerST`
        """

        self._database_url: str = project_settings.DATABASE_URL
        self._engine: AsyncEngine | None = None
        self._session_factory: Callable[[], AsyncSession] | None = None

    def __await__(self) -> Generator[Any, None, Self]:
        """
        Asynchronously initializes the database manager and returns the instance.

        :return: `Self`
            Initialized `AsyncDatabaseManagerST` instance (self)
        """

        return self.initialize().__await__()

    @property
    def engine(self) -> AsyncEngine:
        """
        Returns the SQLAlchemy asynchronous engine.

        :return: `AsyncEngine`
            The SQLAlchemy asynchronous engine instance.

        :raises InitializationError:
            If the engine has not been initialized yet.
        """

        if self._engine is None:
            raise InitializationError(f"Unable to get async_engine: {self.__class__.__name__} is not initialized yet")

        return self._engine

    async def initialize(self) -> Self:
        """
        Asynchronously initializes the database engine and session factory.

        :return: `Self`
            Initialized `AsyncDatabaseManagerST` instance.
        """

        self._engine = create_async_engine(self._database_url, pool_pre_ping=True)
        self._session_factory = sessionmaker(  # type: ignore
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

        return self

    def session(self) -> AsyncContextManager[AsyncSession]:
        """
        Provides an asynchronous session context manager for database requests.
        Session is wrapped with `async_session_error_convert_wrapper`
        so it will convert some db errors based on `src.app.bases.db.exceptions.error_mapping`

        :return: `AsyncContextManager[AsyncSession]`
            An asynchronous context manager for an SQLAlchemy session.

        :raises InitializationError:
            If the session factory has not been initialized yet.
        """

        if self._session_factory is None:
            raise InitializationError(f"Unable to get session: {self.__class__.__name__} is not initialized yet")

        return async_session_error_convert_wrapper(
            self._session_factory(),
            error_mapping=error_mapping
        )
