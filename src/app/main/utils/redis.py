from typing import Any


def convert_for_redis[_KT](mapping: dict[_KT, Any]) -> dict[_KT, Any]:
    """
    Convert values in a mapping to types acceptable for Redis storage.

    :param mapping: `dict[_KT, Any]`
        A dictionary mapping keys to values that are to be stored in Redis.
        The function converts boolean values to integers to ensure compatibility.

    :return: `dict[_KT, Any]`
        A new dictionary with all boolean values converted to integers for Redis compatibility.
    """

    return {key: int(value) if isinstance(value, bool) else value for key, value in mapping.items()}
