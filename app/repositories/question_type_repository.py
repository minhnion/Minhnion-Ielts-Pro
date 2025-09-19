from sqlalchemy.orm import Session, joinedload
from app.models import question_type as question_type_model

class QuestionTypeRepository:
    def get_all(self, db: Session):
        return db.query(question_type_model.QuestionType).all()
    
    def get_by_slug(self, db: Session, slug: str):
        return (
            db.query(question_type_model.QuestionType)
            .options(joinedload(question_type_model.QuestionType.practice_questions))
            .filter(question_type_model.QuestionType.slug == slug)
            .first()
        )

question_type_repo = QuestionTypeRepository()