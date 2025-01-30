from typing import TYPE_CHECKING, Container

from pydantic import ConfigDict, create_model

from src.core.exceptions import NotFoundError

if TYPE_CHECKING:
    from .base import BaseModel, BaseSchema  # type: ignore


def sqlalchemy_to_pydantic[_schemaT: 'BaseSchema'](
        db_model: type['BaseModel'],
        *,
        exclude: Container[str] | None = None,
        config: ConfigDict | None = None,
        bases: tuple[type[_schemaT], ...] | None = None,
        **model_kwargs
) -> type[_schemaT]:
    """
    Converts a SQLAlchemy model to a Pydantic schema dynamically.

    :param db_model: `type[BaseModel]`
        SQLAlchemy database model to convert.

    :param exclude: `Container[str] | None`
        (Optional) A collection of field names to exclude from the schema.

    :param config: `ConfigDict | None`
        (Optional) Pydantic model configuration.

    :param bases: `tuple[type[_schemaT], ...] | None`
        (Optional) Base classes for the generated Pydantic schema.

    :param model_kwargs: `dict`
        Additional keyword arguments for Pydantic model creation.

    :raises NotFoundError:
        If the table associated with the SQLAlchemy model is not found, or if a column does not have a valid type.

    :return: `type[_schemaT]`
        Dynamically generated Pydantic model class.
    """

    table = db_model.metadata.tables[db_model.__tablename__]
    fields = {}

    for column in table.columns:
        column_name = column.name
        if exclude is not None and column_name in exclude:
            continue

        if hasattr(column.type, "impl") and hasattr(column.type.impl, "python_type"):
            python_type = column.type.impl.python_type
        elif hasattr(column.type, "python_type"):
            python_type = column.type.python_type
        else:
            raise NotFoundError(f"Column has no type impl or python_type (Column {column})")

        fields[column_name] = (python_type, ...) if not column.nullable else (python_type | None, None)

    return create_model(  # type: ignore
        db_model.__name__,
        __config__=config,
        __base__=bases,
        **model_kwargs,
        **fields
    )
