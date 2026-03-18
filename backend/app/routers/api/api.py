from fastapi import APIRouter
from app.routers.api import (departments)

api_router = APIRouter(prefix="/api/endpoints", tags=["API"])
api_router.include_router(departments.router)
