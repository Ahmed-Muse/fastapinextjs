from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import sessions as deps
from app.schemas.departments import DepartmentOut, DepartmentCreate, DepartmentUpdate
from app.crud.crud import department_crud

router = APIRouter()

@router.get("/Read", response_model=list[DepartmentOut])
def departments(skip: int = 0, limit: int = 100, db: Session = Depends(deps.get_db)):
    return department_crud.get_items(db, skip, limit)

@router.post("/Create", response_model=DepartmentOut)
def create_department(department: DepartmentCreate, db: Session = Depends(deps.get_db)):
    return department_crud.create_item(db, department)

@router.get("/Read/{id}", response_model=DepartmentOut)
def get_department(id: int, db: Session = Depends(deps.get_db)):
    obj = department_crud.get(db, id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj

@router.patch("/Update/{id}", response_model=DepartmentOut)
def update_department(id: int, data: DepartmentUpdate, db: Session = Depends(deps.get_db)):
    obj = department_crud.get(db, id)
    if not obj:
        raise HTTPException(404, "Not found")
    return department_crud.update_item(db, obj, data)

@router.delete("/Delete/{id}")
def delete_department(id: int, db: Session = Depends(deps.get_db)):
    obj = department_crud.delete_item(db, id)
    if not obj:
        raise HTTPException(404, "Not found")
    return {"ok": True}