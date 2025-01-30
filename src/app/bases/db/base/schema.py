from typing import Any

from pydantic import BaseModel


class BaseSchema(BaseModel):
    """
    A base schema class for Pydantic models with additional utility methods.
    """

    def to_json_dict(self, *args, **kwargs) -> dict[str, Any]:
        """
        Converts the schema instance to a JSON-compatible dictionary.

        :param args: `tuple`
            Additional positional arguments for the `model_dump` method.

        :param kwargs: `dict`
            Additional keyword arguments for the `model_dump` method.

        :return: `dict[str, Any]`
            A dictionary representation of the schema in JSON format.
        """
        return self.model_dump(mode="json", *args, **kwargs)

    def to_model_instance[_modelT: BaseModel](self, model: type[_modelT]) -> _modelT:
        """
        Converts the schema instance into a model instance.

        :param model: `type[_T]`
            The model class to instantiate.

        :return: `_T`
            An instance of the specified model class.
        """

        return model(**self.model_dump())

    def convert_to[_schemaT: BaseSchema](self, schema_cls: type[_schemaT], **fields) -> _schemaT:
        """
        Converts the schema instance to another schema class.

        :param schema_cls: `type[_schemaT]`
            The target schema class to convert to.

        :param fields: `dict`
            Additional fields to include in the converted schema.

        :return: `_schemaT`
            An instance of the target schema class.
        """
        return schema_cls(**{
            **self.model_dump(),
            **fields
        })
