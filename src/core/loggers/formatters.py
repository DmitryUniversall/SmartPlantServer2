import logging


class CustomLogFormatter(logging.Formatter):
    """
    A custom logging formatter that provides detailed information in the log output.

    Static attributes:
    - `format_`: `str`
        The log format string.
    """

    format_ = """[%(asctime)s]\npath = %(pathname)s\nlevel = %(levelname)s\nlogger = %(name)s\nplace = %(filename)s; in '%(funcName)s'; line %(lineno)d\nmessage = %(message)s\n"""

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats the log record to `format_`.

        :param record: `LogRecord`
            The log record to be formatted.

        :return: `str`
            The formatted log message.
        """

        log_fmt = self.format_
        formatter = logging.Formatter(fmt=log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class ColoredLogFormatter(CustomLogFormatter):
    """
    A custom logging formatter that provides color-coded log output.

    Static attributes:
    - `grey`: `str`
        ANSI escape code for grey color.
    - `yellow`: `str`
        ANSI escape code for yellow color.
    - `red`: `str`
        ANSI escape code for red color.
    - `bold_red`: `str`
        ANSI escape code for bold red color.
    - `reset`: `str`
        ANSI escape code to reset color.
    """

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the LogFormatterColor instance.

        :param args: `Tuple`
            Additional positional arguments to be passed to parent class.

        :param kwargs: `Dict`
            Additional keyword arguments to be passed to parent class.
        """

        super().__init__(*args, **kwargs)
        self.FORMATS = {
            logging.DEBUG: self.grey + self.format_ + self.reset,
            logging.INFO: self.grey + self.format_ + self.reset,
            logging.WARNING: self.yellow + self.format_ + self.reset,
            logging.ERROR: self.red + self.format_ + self.reset,
            logging.CRITICAL: self.bold_red + self.format_ + self.reset
        }

    def format(self, record):
        """
        Formats the log record using color-coded format strings.

        :param record: `LogRecord`
            The log record to be formatted.

        :return: `str`
            The formatted log message.
        """

        log_fmt = self.FORMATS[record.levelno]
        formatter = logging.Formatter(fmt=log_fmt, datefmt='%Y-%m-%d %H:%M:%S')
        return formatter.format(record)


class ConsoleLogFormatter(ColoredLogFormatter):
    """
    A console-specific logging formatter with a simplified format.

    Static attributes:
    - `format_`: `str`
        The console log format string.
    """

    format_ = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"


class FileLogFormatter(CustomLogFormatter):
    """
    A file-specific logging formatter with a detailed format.

    Static attributes:
    - `format_`: `str`
        The file log format string.
    """

    format_ = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s; in '%(funcName)s':%(lineno)d)"
