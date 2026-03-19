from fastapi import APIRouter
from app.api.v1.endpoints import departments
from app.routers import (user_feedbacks)

api_router = APIRouter()

api_router.include_router(user_feedbacks.router,prefix="/user", tags=["User Feedbacks"])
api_router.include_router(departments.router, prefix="/departments", tags=["Departments"])