from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.schemas.departments import DepartmentOut
from app.models.departments import DepartmentsModel

#from app.services import department_service

router = APIRouter()

@router.get("/feedbacks", response_model=list[DepartmentOut])
def user_feedbacks(db: Session = Depends(get_db)):
    departments=db.query(DepartmentsModel).all()
    return departments
