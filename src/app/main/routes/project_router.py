from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute
from .auth import auth_router

# Make sure that all endpoints implement base server interface
assert auth_router.route_class is ApplicationResponseApiRoute

project_router = APIRouter()
project_router.include_router(auth_router, prefix="/auth")
