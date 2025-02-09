from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute

storage_router = APIRouter(route_class=ApplicationResponseApiRoute)
