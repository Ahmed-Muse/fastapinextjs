from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import sessions as deps
from app.schemas.departments import DepartmentOut, DepartmentCreate, DepartmentUpdate
from app.services.departments import department_service

router = APIRouter(prefix="/departments", tags=["Departments"])

@router.get("/", response_model=list[DepartmentOut])
def list_departments(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return department_service.crud.get_items(db, skip, limit)


@router.post("/", response_model=DepartmentOut)
def create_department(data: DepartmentCreate, db: Session = Depends(deps.get_db)):
    return department_service.crud.create_item(db, data)


@router.get("/{id}", response_model=DepartmentOut)
def get_department(id: int, db: Session = Depends(deps.get_db)):
    return department_service.get_or_404(db, id)


@router.patch("/{id}", response_model=DepartmentOut)
def update_department(id: int, data: DepartmentUpdate, db: Session = Depends(deps.get_db)):
    obj = department_service.get_or_404(db, id)
    return department_service.crud.update_item(db, obj, data)


@router.delete("/{id}")
def delete_department(id: int, db: Session = Depends(deps.get_db)):
    obj = department_service.get_or_404(db, id)
    department_service.crud.delete_item(db, obj)
    return {"ok": True}