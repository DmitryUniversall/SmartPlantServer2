from src.app.main.http import ApplicationJsonResponse, SuccessResponse
from ..router import utils_router


@utils_router.get("/ping/")
async def ping_route() -> ApplicationJsonResponse:
    return SuccessResponse[str](data={"result": "Pong"})
