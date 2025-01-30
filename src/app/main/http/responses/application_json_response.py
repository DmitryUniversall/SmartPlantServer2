from typing import Any

from fastapi.responses import JSONResponse

from src.app.main.models_global import ApplicationResponsePayload


class ApplicationJsonResponse[_contentT: Any](JSONResponse):
    """
    A custom FastAPI response class for handling JSON responses with a specific payload structure.
    """

    def __init__(self, *, content: ApplicationResponsePayload[_contentT], **kwargs) -> None:
        """
        Initializes the response with the given payload.

        :param content: `ApplicationResponsePayload[_contentT]`
            The content of the response, which should be an instance of `ApplicationResponsePayload`.

        :param kwargs: `**kwargs`
            Additional keyword arguments passed to the parent class `JSONResponse`.
        """

        self.payload = content
        super().__init__(content, **kwargs)

    def render(self, content: ApplicationResponsePayload[_contentT]) -> bytes:
        """
        Renders the content into a JSON-encoded byte string.

        :param content: `ApplicationResponsePayload[_contentT]`
            The payload to be serialized into a JSON string.

        :return: `bytes`
            The JSON-encoded byte string of the payload.
        """

        return content.model_dump_json().encode(self.charset)
