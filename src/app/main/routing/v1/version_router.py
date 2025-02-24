from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute
from src.app.main.routing.v1.auth import auth_router
from src.app.main.routing.v1.storage import storage_router

# Make sure that all endpoints implement base server interface
assert auth_router.route_class is ApplicationResponseApiRoute
assert storage_router.route_class is ApplicationResponseApiRoute

v1_router = APIRouter(route_class=ApplicationResponseApiRoute)
v1_router.include_router(auth_router, prefix="/auth")
v1_router.include_router(storage_router, prefix="/storage")
