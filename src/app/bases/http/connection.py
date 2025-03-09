import asyncio
import logging
from contextlib import asynccontextmanager

from starlette.requests import Request

_logger = logging.getLogger(__name__)


@asynccontextmanager
async def cancel_on_disconnect(request: Request):
    """
    Async context manager for async code that needs to be canceled if client disconnects.
    """

    disconnect_task = asyncio.create_task(watch_disconnect(request))

    try:
        yield
    except Exception as e:
        raise e
    finally:
        disconnect_task.cancel()

        try:
            await disconnect_task
        except asyncio.CancelledError:
            pass


async def watch_disconnect(request: Request):
    while True:
        try:
            message = await request.receive()

            if message['type'] == 'http.disconnect':
                client = f'{request.client.host}:{request.client.port}' if request.client else '-:-'
                _logger.info(f'{client} - "{request.method} {request.url.path}" 499 DISCONNECTED')
                raise asyncio.CancelledError()
        except asyncio.CancelledError:
            break
        except Exception:
            raise
