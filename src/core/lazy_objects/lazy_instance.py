from src.core.lazy_objects.lazy_object import LazyObject


class LazyInstance[_T](LazyObject[_T]):
    def __init__(self, object_name: str, *args, **kwargs) -> None:
        """
        Initializes the LazyInstance instance.

        :param object_name: `str`
            The name of the lazy object.

        :param args: `Tuple`
            The positional arguments to be passed when creating the instance.

        :param kwargs: `Dict`
            The keyword arguments to be passed when creating the instance.
        """

        super().__init__(object_name)

        self.args = args
        self.kwargs = kwargs

    def get_object(self) -> _T:
        """
        Retrieves and returns the actual value of the lazy object, creating an instance with provided arguments.

        :return: `_T`
            The actual value of the lazy object.
        """

        obj = super().get_object()
        return obj(*self.args, **self.kwargs)  # type: ignore
