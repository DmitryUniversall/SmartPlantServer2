import logging
from http import HTTPStatus

from starlette.requests import Request

from src.app.bases.db import BaseModel
from src.app.bases.exceptions import AbstractErrorHandler
from src.app.main.http.responses import ApplicationJsonResponse
from src.app.main.models_global import ApplicationResponsePayload
from src.core.state import project_settings
from src.core.utils.types import JsonDict

_logger = logging.getLogger(__name__)


@AbstractErrorHandler.as_error_handler(exception_cls=BaseModel.DoesNotExist)
async def does_not_exist_exception_handler(_: Request, error: BaseModel.DoesNotExist, **__) -> ApplicationJsonResponse:
    _logger.debug(f"Sending HTTP 404 on error: {error.__class__.__name__}: {error}")

    return ApplicationJsonResponse(
        content=ApplicationResponsePayload[JsonDict](
            ok=False,
            application_status_code=project_settings.APPLICATION_STATUS_CODES.GENERIC_ERRORS.NOT_FOUND,
            message="Object or sub-object does not exist",
            data=None
        ),
        status_code=HTTPStatus.NOT_FOUND
    )
