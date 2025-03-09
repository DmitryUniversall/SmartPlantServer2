from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute

users_router = APIRouter(route_class=ApplicationResponseApiRoute)
