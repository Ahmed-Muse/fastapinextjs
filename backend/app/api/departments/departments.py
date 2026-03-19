from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.sessions import get_db
from app.schemas.departments import DepartmentOut
from app.models.departments import DepartmentsModel

from sqlalchemy.orm import Session
from app.models.departments import DepartmentsModel
from app.schemas.departments import DepartmentCreate, DepartmentUpdate

#from app.services import department_service

router = APIRouter()

@router.get("/", response_model=list[DepartmentOut])
def list_departments(db: Session = Depends(get_db)):
    departments=db.query(DepartmentsModel).all()
    return departments


def get_department(db: Session, department_id: int):
    return db.query(DepartmentsModel).filter(DepartmentsModel.id == department_id).first()

def get_departments(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DepartmentsModel).offset(skip).limit(limit).all()

def create_department(db: Session, department: DepartmentCreate):
    db_department = DepartmentsModel(**department.model_dump())
    db.add(db_department)
    db.commit()
    db.refresh(db_department)
    return db_department

def update_department(db: Session, department_id: int, department_data: DepartmentUpdate):
    db_dept = db.query(DepartmentsModel).filter(DepartmentsModel.id == department_id).first()
    if db_dept:
        update_data = department_data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_dept, key, value)
        db.commit()
        db.refresh(db_dept)
    return db_dept

def delete_department(db: Session, department_id: int):
    db_dept = db.query(DepartmentsModel).filter(DepartmentsModel.id == department_id).first()
    if db_dept:
        db.delete(db_dept)
        db.commit()
        return True
    return False