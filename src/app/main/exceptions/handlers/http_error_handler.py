from starlette.exceptions import HTTPException
from starlette.requests import Request

from src.app.bases.exceptions import AbstractErrorHandler
from src.app.main.http.responses import ApplicationJsonResponse
from src.app.main.models_global import ApplicationResponsePayload
from src.core.state import project_settings
from src.core.utils.types import JsonDict


@AbstractErrorHandler.as_error_handler(exception_cls=HTTPException)
async def http_exception_handler(_: Request, error: HTTPException, **__) -> ApplicationJsonResponse:
    return ApplicationJsonResponse(
        content=ApplicationResponsePayload[JsonDict](
            ok=200 <= error.status_code < 300,
            application_status_code=project_settings.APPLICATION_STATUS_CODES.NOT_SPECIFIED,
            message=str(error),
            data={
                "detail": error.detail
            }
        ),
        status_code=error.status_code,
        headers=error.headers
    )
