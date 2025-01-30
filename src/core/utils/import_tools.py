import sys
from importlib import import_module
from typing import Any


def cached_import(module_path: str, object_name: str) -> Any:
    """
    Imports an object from a module, using a cache if the module is already imported.

    :param module_path: `str`
        The path of the module to import.

    :param object_name: `str`
        The name of the object to retrieve from the module.

    :return: `Any`
        The imported object.

    :raises ImportError:
        If the object cannot be found in the module.
    """

    # Check whether the module is already loaded and fully initialized
    module = sys.modules.get(module_path)
    spec = getattr(module, "__spec__", None)

    if not (module and spec and not getattr(spec, "_initializing", False)):
        module = import_module(module_path)

    try:
        return getattr(module, object_name)
    except AttributeError as error:
        raise ImportError(f"Attribute '{object_name}' is not defined in module '{module_path}'") from error


def import_object(object_path: str) -> Any:
    """
    Imports an object using its full path in dot notation (e.g., "module.submodule.object").

    :param object_path: `str`
        The full dot-separated path of the object to import.

    :return: `Any`
        The imported object.

    :raises ImportError:
        If the object path is invalid or the object cannot be found.
    """

    try:
        module_path, object_name = object_path.rsplit(".", 1)
    except ValueError as error:
        raise ImportError(f"'{object_path}' is not a valid module path.") from error

    return cached_import(module_path=module_path, object_name=object_name)
