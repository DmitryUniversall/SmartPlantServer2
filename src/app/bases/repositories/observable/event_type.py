from enum import Enum


class RepositoryEventType(Enum):
    PRE_CREATE = "pre_create"
    POST_CREATE = "post_create"
    PRE_UPDATE = "pre_update"
    POST_UPDATE = "post_update"
    PRE_DELETE = "pre_delete"
    POST_DELETE = "post_delete"
    PRE_BULK_UPDATE = "pre_bulk_update"
    POST_BULK_UPDATE = "post_bulk_update"
    PRE_BULK_CREATE = "pre_bulk_create"
    POST_BULK_CREATE = "post_bulk_create"
