from typing import TypedDict

from src.core.utils.types import JsonDict


class StorageChannelMessageCreateTD(TypedDict):
    user_id: int
    sender_name: str
    target_name: str
    channel_name: str
    data: JsonDict


class StorageDirectMessageCreateTD(TypedDict):
    user_id: int
    sender_name: str
    target_name: str
    data: JsonDict
