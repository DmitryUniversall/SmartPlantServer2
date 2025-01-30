from .base import BaseApplicationError


class NoneObjectError(BaseApplicationError):
    pass


class InitializationError(BaseApplicationError):
    pass


class CancelOperation(BaseApplicationError):
    pass


class ConfigurationError(BaseApplicationError):
    pass


class NotFoundError(BaseApplicationError):
    pass


class AlreadyExistsError(BaseApplicationError):
    pass


class BadVersionError(BaseApplicationError):
    pass
