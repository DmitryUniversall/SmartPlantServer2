from starlette.requests import Request

from src.app.bases.exceptions import AbstractErrorHandler
from src.app.main.exceptions import ApplicationHTTPException
from src.app.main.http.responses import ApplicationJsonResponse


@AbstractErrorHandler.as_error_handler(exception_cls=ApplicationHTTPException)
async def application_http_exception_handler(_: Request, error: ApplicationHTTPException, **__) -> ApplicationJsonResponse:
    return ApplicationJsonResponse(
        content=error.payload,
        headers=error.headers,
        status_code=error.status_code
    )
