from enum import Enum


class StorageDirectMessageIntent(Enum):
    REQUEST = "request"
    RESPONSE = "response"
    OTHER = "other"
