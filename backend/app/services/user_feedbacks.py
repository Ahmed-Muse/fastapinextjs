from app.services.base import BaseService
from app.crud.crud import user_feedback_crud
class UserFeedbackService(BaseService):
    pass

user_feedback_service = UserFeedbackService(user_feedback_crud)