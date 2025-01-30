import asyncio
import json
from typing import Callable, Iterable, Any


class DotDict(dict[str, Any]):
    """
    A dictionary-like class where attributes are accessed using dot notation.

    Notes:
    - WARNING: If replace_with_dotdict=True, all values that have type `dict` will be replaced with `DotDict`.
    """

    __delattr__ = dict.__delitem__  # type: ignore

    def __init__(
            self,
            init_data: dict[str, Any] | None = None,
            replace_with_dotdict: bool = True
    ) -> None:
        """
        Initialize DotDict instance

        :param init_data: `dict[str, Any] | None`
            (Optional) Init data to be added to DotDict.

        Notes:
            WARNING: All values that have type `dict` will be replaced with `DotDict`
        """

        super(DotDict, self).__init__(**(init_data if init_data is not None else {}))

        self._replace_with_dotdict = replace_with_dotdict

        if self._replace_with_dotdict:
            for key, value in self.items():
                if type(value) is dict:
                    setattr(self, key, DotDict(value))

    @property
    def replace_with_dotdict(self) -> bool:
        return self._replace_with_dotdict

    @replace_with_dotdict.setter
    def replace_with_dotdict(self, value: bool) -> None:
        self._replace_with_dotdict = bool(value)

    def __setattr__(self, key: str, value: Any) -> None:
        """
        Overrides the attribute setter to handle `dict` values by converting them to `DotDict`.

        :param key: `str`
            The attribute key.

        :param value: `Any`
            The attribute value.
        """

        if key.startswith("_"):
            self.__dict__[key] = value
            return

        if type(value) is dict and self.replace_with_dotdict:
            dict.__setitem__(self, key, DotDict(value))
        else:
            dict.__setitem__(self, key, value)

    def __getattr__(self, item: str) -> Any:
        """
        Overrides the attribute getter to access values using dot notation.

        :param item: `str`
            The attribute name.

        :return: `Any`
            The attribute value.

        :raises AttributeError: If the attribute is not found.
        """

        try:
            return super(DotDict, self).__getitem__(item)
        except KeyError as error:
            raise AttributeError(f"{self.__class__.__name__} has no attribute '{item}'") from error

    def find(self, key: str) -> Any:
        """
        Recursively searches for a key in the DotDict and returns its corresponding value.

        :param key: `str`
            The key to search for.

        :return: `Any`
            The value corresponding to the key if found, otherwise None.
        """

        return find_in_dict(self, key)


class AsyncObservableMixin[_KT, _VT]:
    """
    Mixin class that provides asynchronous waiting for key-value pairs to be added.
    To use this mixin, parent class must implement `__getitem__` and `__setitem__` methods
    """

    def __init__(self) -> None:
        """
        Initializes an empty AsyncDict with no pending futures.
        """

        self._pending: dict[_KT, asyncio.Future[_VT]] = {}
        self._global_pending: list[asyncio.Future[_VT]] = []

    def __contains__(self, item: _KT) -> bool:
        return super().__contains__(item)  # type: ignore

    def __getitem__(self, item: _KT) -> _VT:
        return super().__getitem__(item)  # type: ignore

    def __setitem__(self, key: _KT, value: _VT) -> None:
        """
        Sets the item in the dictionary and notifies any waiting futures.

        :param key: `_KT`
            The key to set in the dictionary.
        :param value: `_VT`
            The value to set for the given key.
        """

        super().__setitem__(key, value)  # type: ignore
        self._notify(key, value)

    def _notify(self, key: _KT, value: _VT) -> None:
        """
        Notifies the waiting futures that the value for the given key is available.

        :param key: `_KT`
            The key that has a new value.

        :param value: `_VT`
            The new value for the given key.
        """

        if key in self._pending:
            future = self._pending.pop(key)
            if not future.done():
                future.set_result(value)

        while self._global_pending:
            future = self._global_pending.pop(0)
            if not future.done():
                future.set_result(value)

    def _register_future(self, future: asyncio.Future, key: _KT | None = None) -> None:
        """
        Registers a future to be notified when a value for the given key is available.

        :param future: `asyncio.Future`
            The future to register.

        :param key: `_KT | None`
            The key to register the future for. If None, the future will be notified for any key.
        """

        if key is not None:
            self._pending[key] = future
        else:
            self._global_pending.append(future)

    async def wait_for(
            self,
            key: _KT | None = None,
            filter_func: Callable[[_VT], bool] | None = None,
            timeout: float | None = None
    ) -> _VT:
        """
        Waits for a value to be available in the dictionary for the given key and optionally filters it.

        :param key: `_KT | None`
            The key to wait for. If None, wait for any key.

        :param filter_func: `Callable[[_VT], bool] | None`
            An optional function to filter the values.

        :param timeout: `float | None`
            The maximum time to wait for the value in seconds. If None, wait indefinitely.

        :return: `_VT`
            The value for the given key if found and the filter function returns True, otherwise None.

        :raises: `asyncio.TimeoutError`
            If the timeout is reached before the value is available.
        """

        if key is not None and key in self:
            value = self[key]
            if filter_func is None or filter_func(value):
                return value

        future: asyncio.Future[_VT] = asyncio.Future()
        self._register_future(future, key)

        async with asyncio.timeout(timeout):
            while True:
                value = await future
                if filter_func is None or filter_func(value):
                    return value

                future = asyncio.Future()
                self._register_future(future, key)


class AsyncObservableDict[_KT, _VT](AsyncObservableMixin, dict[_KT, _VT]):
    """
    A dictionary class that supports asynchronous observation of key-value pairs.
    """


def find_in_dict[_KT, _VT](dict_: dict[_KT, _VT], key: _KT) -> _VT | None:
    """
    Recursively searches for a key in a nested dictionary and returns its corresponding value.

    :param dict_: `dict[_KT, _VT]`
        The dictionary to search.

    :param key: `_KT`
        The key to search for.

    :return: `_VT | None`
        The value corresponding to the key if found, otherwise None.
    """

    if (value := dict_.get(key, None)) is not None:
        return value

    for val in dict_.values():
        if isinstance(val, dict) and (value := find_in_dict(val, key)) is not None:
            return value


def find_in_array[_T](array: Iterable[_T], check: Callable[[_T], bool]) -> _T | None:
    """
    Finds an object in the array using check func

    :param array: `Iterable[_T]`
        Array of where to look for an object

    :param check: `Callable[[_T], bool]`
        Check function

    :return: `_T | None`
        Returns an object if found otherwise None
    """

    for element in array:
        if check(element):
            return element


def clear_none_values[_KT, _VT](dict_: dict[_KT, _VT | None]) -> dict[_KT, _VT]:
    """
    Cleans dict from keys whose values are None

    :param dict_: `dict[_KT, _VT]`
        Dict to be cleaned

    :return: `dict[_KT, _VT]`
        Copy of original dict, but without keys whose values are None
    """

    return {key: value for key, value in dict_.items() if value is not None}


def exclude_from_dict[_KT, _VT](dict_: dict[_KT, _VT], *exclude: *tuple[_KT, ...]) -> dict[_KT, _VT]:
    """
    Excludes specified keys from dict

    :param dict_: `dict[_KT, _VT]`
        Dict, where keys should be removed from

    :param exclude: `*tuple[_KT, ...]`
        Keys to be removed

    :return: `dict[_KT, _VT]`
        Copy of original dict, but without specified keys
    """

    return {key: value for key, value in dict_.items() if key not in exclude}


def replace_substring(original_string: str, start_index: int, end_index: int, replacement_substring: str) -> str:
    """
    Replaces the substring in original_string for indexes from start_index to end_index with replacement_substring

    :param original_string: `str`
        String in which to replace

    :param start_index: `int`
        Start replacement index

    :param end_index: `int`
        End replacement index

    :param replacement_substring: `str`
        String to insert

    :return: `str`
        Modified string

    :raises:
        :raise IndexError: If start index or end index is invalid
    """

    if (start_index < 0 or start_index >= len(original_string)) or (
            end_index < 0 or end_index > len(original_string)) or (start_index > end_index):
        raise IndexError("Invalid start or end index.")

    return original_string[:start_index] + replacement_substring + original_string[end_index:]


def for_each[_T](func: Callable, iterable: Iterable[_T]) -> None:
    """
    Apply a function to each element of iterable.

    :param func: Callable
        The function to apply to each element of the iterable.

    :param iterable: Iterable[_T]
        Iterable, whose elements will be passed to the function.

    :raises:
        :raise TypeError: If the provided argument is not iterable.
    """

    tuple(map(func, iterable))


def safe_json(data: str | bytes, **kwargs) -> dict[str, Any] | None:
    """
    Apply a function to each element of iterable.

    :param data: `str | bytes`
        The function to apply to each element of the iterable.

    :param kwargs: `dict[str, Any]`
        Keyword arguments to be passed to the `json.loads` function.

    :return: `dict[str, Any] | None`
        Deserialized JSON if it's valid, otherwise None.
    """

    try:
        return json.loads(data, **kwargs)
    except json.JSONDecodeError:
        return None
