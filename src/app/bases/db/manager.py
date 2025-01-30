from abc import ABC, abstractmethod
from typing import AsyncContextManager, Self

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from .async_session_wrappers import transaction_session


class AbstractAsyncDatabaseManager(ABC):
    """
    An abstract base class for managing asynchronous database interactions with SQLAlchemy.
    """

    @property
    @abstractmethod
    def engine(self) -> AsyncEngine:
        """
        Abstract property that must return an asynchronous SQLAlchemy engine.

        :return: `AsyncEngine`
            The asynchronous engine used for database interactions.
        """

    @abstractmethod
    def session(self) -> AsyncContextManager[AsyncSession]:
        """
        Abstract method that must return a context manager for handling database sessions.

        :return: `AsyncContextManager[AsyncSession]`
            A context manager to handle the lifecycle of a database session.
        """

    @abstractmethod
    async def initialize(self) -> Self:
        """
        Abstract method to initialize the database manager.

        :return: `Self`
            The instance of the database manager itself after initialization.
        """

    def transaction(self) -> AsyncContextManager[AsyncSession]:
        """
        Returns a context manager for handling database transactions.

        Wraps the session context manager in a transaction manager,
        ensuring that all operations within the context are automatically committed
        or rolled back in case of an error.

        :return: `AsyncContextManager[AsyncSession]`
            A context manager that provides a transactional database session.
        """

        return transaction_session(self.session())
