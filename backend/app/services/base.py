from fastapi import HTTPException
from sqlalchemy.orm import Session

class BaseService:

    def __init__(self, crud):
        self.crud = crud

    def get_or_404(self, db: Session, id: int):
        obj = self.crud.get(db, id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj