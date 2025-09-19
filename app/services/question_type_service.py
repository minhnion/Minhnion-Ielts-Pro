from sqlalchemy.orm import Session
from fastapi import HTTPException, status 
from app.repositories.question_type_repository import question_type_repo

class QuestionTypeService:
    def get_all(self, db: Session):
        return question_type_repo.get_all(db)
    
    def get_by_slug(self, db: Session, slug: str):
        question_type = question_type_repo.get_by_slug(db, slug)
        if not question_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Question type with slug '{slug}' not found",
            )

        return question_type
    
question_type_service = QuestionTypeService()