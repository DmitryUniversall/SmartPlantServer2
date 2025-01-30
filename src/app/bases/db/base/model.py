from typing import Any

from sqlalchemy.ext.declarative import declarative_base, DeclarativeMeta

from src.app.bases.db.base.schema import BaseSchema
from src.app.bases.db.exceptions import DoesNotExistError
from src.app.bases.db.sqlalchemy_to_pydantic import sqlalchemy_to_pydantic

Base = declarative_base()


class CustomModelMeta(DeclarativeMeta):
    """
    A custom metaclass that adds a `DoesNotExist` exception class to models.
    """

    def __new__(cls, name: str, bases: tuple[type], attrs: dict[str, Any]) -> 'CustomModelMeta':
        """
        Creates a new model class and injects a `DoesNotExist` exception.

        :param name: `str`
            The name of the model class.

        :param bases: `tuple[type]`
            The base classes for the model class.

        :param attrs: `dict[str, Any]`
            The attributes of the model class.

        :return: `CustomModelMeta`
            The newly created model class.
        """

        model_cls = super().__new__(cls, name, bases, attrs)
        setattr(cls, "DoesNotExist", type("DoesNotExist", (DoesNotExistError,), {}))
        return model_cls


class BaseModel[_schemaT: BaseSchema](Base, metaclass=CustomModelMeta):  # type: ignore
    """
    A base model class for SQLAlchemy models with additional utilities.

    Static attributes:
    - `__secured_fields__`: `tuple[str, ...]`
        Fields that should be excluded from Pydantic schemas.

    - `__pk_field__`: `str`
        Primary key field name that can be used in resources etc.
    """

    __abstract__: bool = True
    __secured_fields__: tuple[str, ...] = tuple()
    __pk_field__: str = "id"

    class DoesNotExist(DoesNotExistError):  # Only for type checking; will be replaced by metaclass
        """
        Placeholder for the `DoesNotExist` exception, replaced by the metaclass.
        """

    @classmethod
    def as_pydantic_scheme(
            cls,
            exclude: tuple[str] | None = None,
            bases: tuple[type[_schemaT], ...] | None = None,
            **model_kwargs
    ) -> type[_schemaT]:
        """
        Generates a Pydantic schema for the model.

        :param exclude: `tuple[str] | None`
            (Optional) Fields to exclude from the generated schema.
            By default, `None`.

        :param bases: `tuple[type[_schemaBaseT], ...] | None`
            (Optional) Base classes for the Pydantic schema.
            By default, `None`.

        :param model_kwargs: `dict`
            Additional keyword arguments for the schema generation.

        :return: `type[_schemaBaseT]`
            The generated Pydantic schema class.
        """

        return sqlalchemy_to_pydantic(
            db_model=cls,
            exclude=cls.__secured_fields__ + (exclude if exclude is not None else tuple()),
            bases=bases,
            **model_kwargs
        )

    def to_schema(self, scheme_cls: type[_schemaT], **fields) -> _schemaT:
        """
        Converts the model instance into a Pydantic schema.

        :param scheme_cls: `type[_schemaBaseT]`
            The Pydantic schema class to use for conversion.

        :param fields: `dict`
            Additional fields to include in the schema.

        :return: `_schemaBaseT`
            An instance of the Pydantic schema class.
        """

        return scheme_cls.model_validate({  # parse_obj
            **self.__dict__,
            **fields
        })
