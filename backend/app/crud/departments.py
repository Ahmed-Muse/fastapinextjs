from app.crud.base import CRUDBase
from app.models.departments import DepartmentsModel
from app.schemas.departments import DepartmentCreate, DepartmentUpdate

class CRUDDepartment(CRUDBase[DepartmentsModel, DepartmentCreate, DepartmentUpdate]):
    pass

department_crud = CRUDDepartment(DepartmentsModel)