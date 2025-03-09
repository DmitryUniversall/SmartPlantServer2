from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute
from src.app.main.routing.v1.auth import auth_router
from src.app.main.routing.v1.storage import storage_router
from src.app.main.routing.v1.utils import utils_router
from src.app.main.routing.v1.users import users_router

# Make sure that all endpoints implement base server interface
assert auth_router.route_class is ApplicationResponseApiRoute
assert storage_router.route_class is ApplicationResponseApiRoute
assert utils_router.route_class is ApplicationResponseApiRoute
assert users_router.route_class is ApplicationResponseApiRoute

v1_router = APIRouter(route_class=ApplicationResponseApiRoute)
v1_router.include_router(auth_router, prefix="/auth")
v1_router.include_router(storage_router, prefix="/storage")
v1_router.include_router(utils_router, prefix="/utils")
v1_router.include_router(users_router, prefix="/users")
