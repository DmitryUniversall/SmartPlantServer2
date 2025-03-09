from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute

utils_router = APIRouter(route_class=ApplicationResponseApiRoute)
