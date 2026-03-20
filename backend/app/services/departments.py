from app.services.base import BaseService
from app.crud.crud import department_crud

class DepartmentService(BaseService):
    pass

department_service = DepartmentService(department_crud)