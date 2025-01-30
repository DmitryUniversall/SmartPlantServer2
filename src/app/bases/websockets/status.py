import logging
from functools import wraps

from starlette.websockets import WebSocket, WebSocketState

_logger = logging.getLogger(__name__)


def is_websocket_disconnected(websocket: WebSocket) -> bool:
    """
    Checks if the WebSocket is disconnected.

    :param websocket: `WebSocket`
        The WebSocket instance to check.

    :return: `bool`
        `True` if the WebSocket is disconnected, `False` otherwise.
    """

    return websocket.application_state is WebSocketState.DISCONNECTED or websocket.client_state is WebSocketState.DISCONNECTED


def is_websocket_connected(websocket: WebSocket) -> bool:
    """
    Checks if the WebSocket connection is still active.

    :param websocket: `WebSocket`
        The WebSocket instance to check.

    :return: `bool`
        `True` if the WebSocket is connected, `False` otherwise.
    """

    return not is_websocket_disconnected(websocket)


def ws_return_if_closed(coro):
    """
    A decorator that checks if the WebSocket is closed before invoking the coroutine.
    If the WebSocket is closed or not passed as a keyword argument, the coroutine is not called.

    :param coro: `Callable`
        The coroutine function to wrap.

    :return: `Callable`
        The wrapped coroutine that ensures the WebSocket is connected before execution.
    """

    @wraps(coro)
    async def wrapper(*args, **kwargs):
        websocket = kwargs.get("websocket")

        if websocket is None or not isinstance(websocket, WebSocket):
            _logger.warning(f'[{coro.__name__}]: Websocket argument was not found')
            return
        elif is_websocket_disconnected(websocket):
            _logger.debug(f'[{coro.__name__}]: Websocket closed, so handler will not be called')
            return

        return await coro(*args, **kwargs)

    return wrapper
