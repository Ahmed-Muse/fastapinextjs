from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import sessions as deps
from app.schemas.schemas import UserFeedbackOut, UserFeedbackCreate, UserFeedbackUpdate
from app.services.user_feedbacks import user_feedback_service

router = APIRouter(prefix="/user/feedbacks", tags=["User Feedbacks"])


@router.get("/", response_model=list[UserFeedbackOut])
def list_feedbacks(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return user_feedback_service.crud.get_items(db, skip, limit)


@router.post("/", response_model=UserFeedbackOut)  # ✅ FIXED
def create_feedback(data: UserFeedbackCreate, db: Session = Depends(deps.get_db)):
    return user_feedback_service.crud.create_item(db, data)


@router.get("/{id}", response_model=UserFeedbackOut)
def get_feedback(id: int, db: Session = Depends(deps.get_db)):
    return user_feedback_service.get_or_404(db, id)


@router.patch("/{id}", response_model=UserFeedbackOut)
def update_feedback(id: int, data: UserFeedbackUpdate, db: Session = Depends(deps.get_db)):
    obj = user_feedback_service.get_or_404(db, id)
    return user_feedback_service.crud.update_item(db, obj, data)


@router.delete("/{id}")
def delete_feedback(id: int, db: Session = Depends(deps.get_db)):
    obj = user_feedback_service.get_or_404(db, id)
    user_feedback_service.crud.delete_item(db, obj)
    return {"ok": True}