from src.app.main.http import SuccessResponse, ApplicationJsonResponse
from ..router import main_router


@main_router.get("/index/")
async def index_route() -> ApplicationJsonResponse:
    return SuccessResponse(message="Hello World")
