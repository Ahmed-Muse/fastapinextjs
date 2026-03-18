from pydantic import BaseModel
from .schemas import BaseSchema

class DepartmentBase(BaseSchema):
    name: str
    description: str | None = None

class DepartmentCreate(DepartmentBase):
    pass

class DepartmentUpdate(DepartmentBase):
    pass

class DepartmentOut(DepartmentBase):
    id: int

    class Config:
        from_attributes = True