from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute
from src.app.main.routing.v1 import v1_router

# Make sure that all endpoints implement base server interface
assert v1_router.route_class is ApplicationResponseApiRoute

project_router = APIRouter()
project_router.include_router(v1_router, prefix="/v1")
