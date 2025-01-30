from settings_setup import setup_settings

settings = setup_settings()

import asyncio

import fastapi
import uvicorn

from setup import (
    setup_loggers,
    setup_database,
    setup_routes,
    setup_error_handlers
)


async def _run_uvicorn():
    config = uvicorn.Config(application, host=settings.HOST, port=settings.PORT)
    server = uvicorn.Server(config)
    await server.serve()


async def _setup(app: fastapi.FastAPI) -> None:
    _logger.info(f"Initializing database")
    await setup_database()

    _logger.info(f"Initializing routes")
    await setup_routes(app)

    _logger.info(f"Initializing error handlers")
    await setup_error_handlers(app)

    _logger.info("Successfully initialized FastAPI application")
    await _run_uvicorn()


# Logger initialization
_logger = setup_loggers()
_logger.info(f"Successful logger and settings setup")
_logger.info(f"Starting application with state: {settings.STATE}")

# Run
application = fastapi.FastAPI()
asyncio.run(_setup(application))
