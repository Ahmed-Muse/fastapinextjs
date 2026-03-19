from app.crud.base import CRUDBase
from app.models.database import DepartmentsModel,UserFeedbacksModel
from app.schemas.departments import DepartmentCreate, DepartmentUpdate

class CRUDDepartment(CRUDBase[DepartmentsModel, DepartmentCreate, DepartmentUpdate]):
    pass

department_crud = CRUDDepartment(DepartmentsModel)


class CRUDUserFeedback(CRUDBase[DepartmentsModel, DepartmentCreate, DepartmentUpdate]):
    pass

user_feedback_crud =CRUDUserFeedback(UserFeedbacksModel)