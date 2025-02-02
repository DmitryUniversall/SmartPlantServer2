from http import HTTPStatus
from typing import Any

from .generic_base import GenericApplicationJsonResponse


class SuccessResponse[_contentT: Any](GenericApplicationJsonResponse[_contentT]):
    """
    A response indicating a successful request with HTTP status code 200 (OK).
    """

    default_ok = True
    default_status_code = HTTPStatus.OK
    default_status_info_path = "GENERICS.SUCCESS"


class CreatedResponse[_contentT: Any](GenericApplicationJsonResponse[_contentT]):
    """
    A response indicating a resource has been successfully created with HTTP status code 201 (Created).
    """

    default_ok = True
    default_status_code = HTTPStatus.CREATED
    default_status_info_path = "GENERICS.CREATED"


class UpdatedResponse[_contentT: Any](GenericApplicationJsonResponse[_contentT]):
    """
    A response indicating that a resource has been successfully updated with HTTP status code 200 (OK).
    """

    default_ok = True
    default_status_code = HTTPStatus.OK
    default_status_info_path = "GENERICS.UPDATED"
