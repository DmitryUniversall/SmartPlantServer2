from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute
from .main import main_router

# Make sure that all endpoints implement base server interface
assert main_router.route_class is ApplicationResponseApiRoute

project_router = APIRouter()
project_router.include_router(main_router, prefix="")
