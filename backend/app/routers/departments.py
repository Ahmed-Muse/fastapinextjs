from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.sessions import SessionLocal
from app.schemas.departments import *
#from app.services import department_service

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    return "Hello from departments router"
    return department_service.list_departments(db)
