from typing import Literal

from .intent import StorageDirectMessageIntent
from .schema import StorageDirectMessage


class StorageDirectRequest(StorageDirectMessage):
    intent: Literal[StorageDirectMessageIntent.REQUEST] = StorageDirectMessageIntent.REQUEST
