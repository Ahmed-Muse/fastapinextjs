from typing import Generic, TypeVar, Type, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")

class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):

    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        return db.get(self.model, id)  # ✅ FIXED (no deprecated .query().get)

    def get_items(self, db: Session, skip: int = 0, limit: int = 100) -> List[ModelType]:
        stmt = (
            select(self.model)
            .order_by(self.model.id)  # ✅ stable pagination
            .offset(skip)
            .limit(limit)
        )
        return db.execute(stmt).scalars().all()

    def create_item(self, db: Session, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_item(self, db: Session, db_obj: ModelType, obj_in: UpdateSchemaType) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():  # ✅ cleaner loop
            setattr(db_obj, field, value)

        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete_item(self, db: Session, db_obj: ModelType) -> None:
        db.delete(db_obj)
        db.commit()