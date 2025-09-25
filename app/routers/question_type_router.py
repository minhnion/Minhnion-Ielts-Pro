from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.services.question_type_service import question_type_service
from app.schemas.question_type_schema import QuestionTypeBase, QuestionTypeDetailGroupedSchema
from app.database import SessionLocal

router = APIRouter(
    prefix="/api/v1/question-types",
    tags=["Question Types"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[QuestionTypeBase])
def read_all_question_types(db: Session = Depends(get_db)):
    return question_type_service.get_all(db=db)

@router.get("/{slug}", response_model=QuestionTypeDetailGroupedSchema)
def read_question_type_details(slug: str, db: Session = Depends(get_db)):
    return question_type_service.get_by_slug(db=db, slug=slug)