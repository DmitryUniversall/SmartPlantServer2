from contextlib import contextmanager
from typing import Generator
from src.app.bases.db import BaseModel
from src.app.main.exceptions.http.generics import NotFoundHTTPException


@contextmanager
def fetch_or_404(message: str | None = None) -> Generator[None, None, None]:
    try:
        yield
    except BaseModel.DoesNotExist as error:
        raise NotFoundHTTPException(message=message if message is not None else "Requested object not found") from error
