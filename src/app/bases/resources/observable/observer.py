from typing import Callable, Coroutine

type ResourceEventObserver = Callable[..., Coroutine[None, None, None]]
