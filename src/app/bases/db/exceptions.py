from src.core.exceptions import BaseApplicationError, NotFoundError


class DBError(BaseApplicationError):
    pass


class DoesNotExistError(DBError, NotFoundError):
    pass
