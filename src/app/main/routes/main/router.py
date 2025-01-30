from fastapi import APIRouter

from src.app.main.http import ApplicationResponseApiRoute

main_router = APIRouter(route_class=ApplicationResponseApiRoute)
