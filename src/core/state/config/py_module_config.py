from typing import Any
from importlib import import_module
from src.core.state.config.abc import AbstractConfig


class PyModuleConfig(AbstractConfig):
    """
    Represents a configuration class that uses a Python module for getting settings.

    :param settings_module: `str`
        The name of the Python module containing the settings.
    """

    def __init__(self, settings_module: str) -> None:
        """
        Initializes the PyModuleConfig instance.

        :param settings_module: `str`
            The name or path of the Python module containing the settings.
        """

        self._settings_module_path = settings_module

    def load(self) -> dict[str, Any]:
        """
        Loads the settings module.

        :return: `dict[str, Any]`
            Module vars dict
        """

        return vars(import_module(self._settings_module_path))
