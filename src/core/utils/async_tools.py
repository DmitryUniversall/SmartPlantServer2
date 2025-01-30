import asyncio
from typing import Coroutine, Callable, Any, Iterable

type CoroOrFuture[_T] = Coroutine[Any, Any, _T] | asyncio.Future[_T]


async def gather_all[_T](coros_or_futures: Iterable[CoroOrFuture[_T]]) -> tuple[_T, ...]:
    """
    Gather all coroutines or futures and return their results as a tuple.

    :param coros_or_futures: `list[CoroOrFuture[_T]]`
        An iterable of coroutines or futures to gather.

    :return: `tuple[_T, ...]`
        A tuple containing the results of the gathered coroutines or futures.
    """

    return tuple(await asyncio.gather(*coros_or_futures))


async def wait_with_timeout[_T](
        coro: CoroOrFuture[_T],
        *,
        timeout: float | None = None,
        shield: bool = False
) -> _T:
    """
    Wait for a coroutine with an optional timeout and shielding.

    :param coro: `CoroOrFuture[_T]`
        The coroutine to wait for.

    :param timeout: `float | None`
        (Optional) The timeout in seconds. By default, `None` (no timeout).

    :param shield: `bool`
        (Optional) Whether to shield the coroutine from cancellation. By default, `False`.

    :return: `_T`
        The result of the coroutine.
    """

    return await asyncio.wait_for(asyncio.shield(coro) if shield else coro, timeout=timeout)


async def safe_wait_with_timeout[_T](
        coro: CoroOrFuture[_T],
        *,
        timeout: float | None = None,
        shield: bool = False
) -> tuple[bool, _T | None]:
    """
    Wait for a coroutine without raising asyncio.TimeoutError, returning a success flag and result.

    :param coro: `CoroOrFuture[_T]`
        The coroutine to wait for.

    :param timeout: `float | None`
        (Optional) The timeout in seconds. By default, `None` (no timeout).

    :param shield: `bool`
        (Optional) Whether to shield the coroutine from cancellation. By default, `False`.

    :return: `tuple[bool, _T | None]`
        A tuple containing a success flag and the result of the coroutine (or `None` if timed out).
    """

    try:
        # FIXME: Argument 1 to "wait_with_timeout" has incompatible type "Coroutine[Any, Any, _T] | Future[_T]"; expected "Coroutine[Any, Any, _T | None] | Future[_T | None]"
        return True, await wait_with_timeout(coro, timeout=timeout, shield=shield)  # type: ignore
    except asyncio.TimeoutError:
        return False, None


async def run_in_threadpool[_T](func: Callable[..., _T], *args: object) -> _T:
    """
    Run a function in a thread pool and return its result.

    :param func: `Callable[..., _T]`
        The function to run in the thread pool.

    :param args: `tuple`
        The arguments to pass to the function.

    :return: `_T`
        The result of the function.
    """

    return await asyncio.get_event_loop().run_in_executor(None, func, *args)


async def _call_after[_T](
        coro: CoroOrFuture[_T],
        *,
        after: float
) -> _T:
    """
    Internal helper to wait for a specified time before executing a coroutine.

    :param coro: `CoroOrFuture[_T]`
        The coroutine to execute.

    :param after: `float`
        The time in seconds to wait before executing the coroutine.

    :return: `_T`
        The result of the coroutine.
    """

    await asyncio.sleep(after)
    return await coro


async def call_after[_T](coro: CoroOrFuture[_T], *, after: float) -> asyncio.Task[_T]:
    """
    Schedule a coroutine to be executed after a specified delay.

    :param coro: `CoroOrFuture[_T]`
        The coroutine to execute.

    :param after: `float`
        The time in seconds to wait before executing the coroutine.

    :return: `asyncio.Task[_T]`
        A task that represents the scheduled coroutine.
    """

    return asyncio.create_task(_call_after(coro, after=after))
