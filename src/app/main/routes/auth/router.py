from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute

auth_router = APIRouter(route_class=ApplicationResponseApiRoute)
