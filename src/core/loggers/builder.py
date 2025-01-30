import logging
import os
import sys
from typing import Self

from .formatters import ConsoleLogFormatter, FileLogFormatter


class LoggerBuilder:
    """
    A builder class for creating and configuring loggers.

    Static attributes:
    - `DEFAULT_CONSOLE_LOG_FORMATTER`: `logging.Formatter`
        The default log formatter for console (`ConsoleLogFormatter` by default).

    - `DEFAULT_FILE_LOG_FORMATTER`: `logging.Formatter`
        The default log formatter for files (`FileLogFormatter` by default).
    """

    DEFAULT_CONSOLE_LOG_FORMATTER: logging.Formatter = ConsoleLogFormatter()
    DEFAULT_FILE_LOG_FORMATTER: logging.Formatter = FileLogFormatter()

    def __init__(self, name: str, level: int = logging.INFO) -> None:
        """
        Initializes LoggerBuilder and creates the logger with specified name and level.

        :param name: `str`
            Logger name

        :param level: `int | None`
            (Optional) Log level for logger.
            By default, `logging.INFO`
        """

        self._logger: logging.Logger = logging.getLogger(name)
        self._logger.setLevel(level)

    def enable_console(self, level: int = logging.INFO, formatter: logging.Formatter | None = None) -> Self:
        """
        Adds `logging.StreamHandler` with `sys.stdout` stream to logger, for logs to be displayed in the console

        :param level: `int | None`
            (Optional) Log level for StreamHandler.
            By default, `logging.INFO`

        :param formatter: `logging.Formatter | None`
            (Optional) Formatter for StreamHandler

        :return: `Self`
            LoggerBuilder object (self)
        """

        console_handler = logging.StreamHandler(stream=sys.stdout)
        console_handler.setFormatter(formatter or self.DEFAULT_CONSOLE_LOG_FORMATTER)
        console_handler.setLevel(level)

        self._logger.addHandler(console_handler)
        return self

    def get(self) -> logging.Logger:
        """
        Returns created logger (`logging.Logger`) object

        :return: `logging.Logger`
            Created logger (`logging.Logger`) object
        """

        return self._logger

    def add_file(self,
                 path: str,
                 level: int = logging.INFO,
                 formatter: logging.Formatter | None = None,
                 handler_cls: type[logging.FileHandler] | None = None,
                 encoding: str | None = None,
                 **kwargs) -> Self:
        """
        Adds `logging.FileHandler` to logger, for logs to be saved to the specified file

        :param path: `str`
            Path to log file

        :param level: `int | None`
            (Optional) Log level for FileHandler

        :param handler_cls: `type[logging.FileHandler] | None`
            (Optional) FileHandler class

        :param formatter: `logging.Formatter | None`
            (Optional) Formatter for handler

        :param encoding: `str | None`
            (Optional) Encoding of the log file

        :return: `Self`
            LoggerBuilder object (self)
        """

        os.makedirs(os.path.dirname(path), exist_ok=True)

        if handler_cls is None:
            handler_cls = logging.FileHandler

        info_file_handler = handler_cls(
            filename=path,
            encoding=encoding or "utf-8",
            **kwargs
        )
        info_file_handler.setFormatter(formatter or self.DEFAULT_FILE_LOG_FORMATTER)
        info_file_handler.setLevel(level)

        self._logger.addHandler(info_file_handler)
        return self
