from sqlalchemy.exc import StatementError


class UniqueConstraintFailed(StatementError):
    pass


error_mapping: dict[str, type[StatementError]] = {
    'duplicate entry': UniqueConstraintFailed,
    "UNIQUE constraint failed": UniqueConstraintFailed
}
