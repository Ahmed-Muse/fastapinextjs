from fastapi import APIRouter
from app.routers import (departments, customers, equipment,)

api_router = APIRouter(prefix="/api/endpoints", tags=["API"])
api_router.include_router(departments.router)
