from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import sessions as deps
from app.schemas.departments import DepartmentOut, DepartmentCreate, DepartmentUpdate
from app.crud.crud import department_crud,user_feedback_crud
from app.schemas.schemas import UserFeedbackOut,UserFeedbackCreate,UserFeedbackUpdate

router = APIRouter()

@router.get("/Read", response_model=list[UserFeedbackOut])
def user_feedbacks(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return user_feedback_crud.get_items(db, skip, limit)

@router.post("/Create", response_model=UserFeedbackCreate)
def add_user_feedback(user_feedback: UserFeedbackCreate, db: Session = Depends(deps.get_db)):
    return user_feedback_crud.create_item(db, user_feedback)

@router.get("/Read/{id}", response_model=UserFeedbackOut)
def get_user_feedback(id: int, db: Session = Depends(deps.get_db)):
    obj = user_feedback_crud.get(db, id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj

@router.patch("/Update/{id}", response_model=UserFeedbackOut)
def update_user_feedback(id: int, data: UserFeedbackUpdate, db: Session = Depends(deps.get_db)):
    obj = user_feedback_crud.get(db, id)
    if not obj:
        raise HTTPException(404, "Not found")
    return user_feedback_crud.update_item(db, obj, data)

@router.delete("/Delete/{id}")
def delete_user_feedback(id: int, db: Session = Depends(deps.get_db)):
    obj = user_feedback_crud.delete_item(db, id)
    if not obj:
        raise HTTPException(404, "Not found")
    return {"ok": True}