from typing import Literal

from .intent import StorageDirectMessageIntent
from .schema import StorageDirectMessage


class StorageDirectResponse(StorageDirectMessage):
    intent: Literal[StorageDirectMessageIntent.RESPONSE] = StorageDirectMessageIntent.RESPONSE
